import operator
import threading
from enum import IntEnum
from functools import wraps
from pathlib import Path
from typing import (
    Callable,
    Optional,
    Type,
    TYPE_CHECKING,
    TypeVar,
    ParamSpec,
    Concatenate,
)

from jnius import PythonJavaClass, autoclass, java_method
from kivy import Logger

from adapters.notes.android.annotations import (
    ACTIVITY_CLASS_NAME,
    ACTIVITY_CLASS_NAMESPACE,
    MINDREF_CLASS_NAME,
    MINDREF_CLASS_NAMESPACE,
    UriProtocol,
)

if TYPE_CHECKING:
    from .annotations import (
        ActivityProtocol,
        ContentResolverProtocol,
        ContextProtocol,
        IntentProtocol,
        MindRefUtilsProtocol,
        MindRefUtilsCallbackPyMediator,
    )


# noinspection PyPep8Naming
class MindRefUtilsCallback(PythonJavaClass):
    __javainterfaces__ = [MINDREF_CLASS_NAMESPACE + "$MindRefUtilsCallback"]
    __javacontext__ = "app"

    py_mediator: Callable[[], "MindRefUtilsCallbackPyMediator"]

    """
    Callback passed to MindRefUtils with methods implement Java Interface
    
    Attributes
    ----------
    py_mediator
        Flexible callable that handle various call signatures. One commonality is all receive a int key
    """

    def __init__(self, py_mediator: Callable[[], "MindRefUtilsCallbackPyMediator"]):
        super().__init__()
        self.py_mediator = py_mediator

    @java_method("(ILjava/lang/String;)V", name="onComplete")
    def onCompleteCreateCategory(self, key: int, category: str):
        self.py_mediator()(key, category)

    @java_method("(I[Ljava/lang/String;)V", name="onComplete")
    def onCompleteGetCategories(self, key: int, categories: list[str]):
        self.py_mediator()(key, categories)

    @java_method("(I)V", name="onComplete")
    def onCompleteCopyStorage(self, key: int):
        self.py_mediator()(key)

    @java_method("(I)V")
    def onFailure(self, key: int):
        # Indicate a failure by making negating the key
        self.py_mediator()(-key)


class ActivityResultCode(IntEnum):
    RESULT_OK = -1
    RESULT_CANCELLED = 0
    RESULT_FIRST_USER = 1


# noinspection PyPep8Naming,PyUnusedLocal
class OnDocumentCallback(PythonJavaClass):
    """PythonActivity (Kivy Built-in) calls this after User has selected folder with Android Document Picker"""

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + "$ActivityResultListener"]
    __javacontext__ = "app"

    def __init__(
        self,
        py_mediator: Callable[[], "MindRefUtilsCallbackPyMediator"],
        activity_code: int,
    ):
        """

        Parameters
        ----------
        py_mediator
        activity_code : int
            Since result comes from PythonActivity, we can't have to inject the activity code here
        """
        super().__init__()
        self.py_mediator = py_mediator
        self.activity_code = activity_code

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(
        self, requestCode: int, resultCode: "ActivityResultCode", result_data
    ):
        tree_uri: UriProtocol = result_data.getData()
        Logger.debug(
            f"OnDocumentCallback: Selected uri - {tree_uri.toString()} - {tree_uri.getPath()}"
        )
        self.py_mediator()(self.activity_code, tree_uri.toString())


P = ParamSpec("P")
F = TypeVar("F")


# noinspection PyPep8Naming
class AndroidStorageManager:
    _lock = threading.Lock()
    _utils_cls_static: Optional[Type["MindRefUtilsProtocol"]] = None
    _utils_cls: Optional["MindRefUtilsProtocol"] = None
    _prompt_folder_callback: Optional[Callable[[str], None]] = None
    _prompt_folder_callback_java: Optional["OnDocumentCallback"] = None
    _mindref_callback_java: Optional["MindRefUtilsCallback"] = None
    _mindref_callback_py_mediator: Optional["MindRefUtilsCallbackPyMediator"] = None

    """
    Orchestrates interacting with PythonActivity (Kivy) and MindRefUtils
    
    Attributes
    ----------
    _lock
        Thread lock
    _utils_cls_static
        Class definition of MindRefUtils
    _utils_cls
        Instance of MindRefUtils
    _prompt_folder_callback
        Python callback for prompt_for_folder 
    _prompt_folder_callback_java
        Java callback which call _prompt_folder_callback
    _mindref_callback_java
        MindRefUtilsCallback
    _mindref_callback_py_mediator
        This flexible callable will be responsible for handling variety of parameters from Java side.
    """

    @classmethod
    def _get_mindref_utils_static_cls(cls) -> Type["MindRefUtilsProtocol"]:
        """Autoclass MindRefUtils Java class. Keep the definition, but do not initialize"""
        if cls._utils_cls_static is None:
            cls._utils_cls_static = autoclass(MINDREF_CLASS_NAME)
        return cls._utils_cls_static

    @classmethod
    def _get_mindref_utils_cls(
        cls, externalStorageRoot: str, appStorageRoot: str, context: "ContextProtocol"
    ) -> "MindRefUtilsProtocol":
        """
        Get an instance of Java MindRefUtils. Subsequent invocations will be cached, depending on storage locations

        Parameters
        ----------
        externalStorageRoot
            str, external storage location str form, but derived from URI
        appStorageRoot
            str, storage for the app that we control
        context
            ContextProtocol, provided from `mActivity.getContext()`

        Returns
        -------
        Initialized instance of MindRefUtils Java
        """
        if cls._utils_cls is None:
            mrUtilsCls = cls._get_mindref_utils_static_cls()
            mrUtils = mrUtilsCls(externalStorageRoot, appStorageRoot, context)
            cls._utils_cls = mrUtils
            return cls._utils_cls
        else:
            # See if our cached instance has same parameters
            cs = cls._utils_cls
            if not all(
                operator.eq(getattr(cs, attr), val)
                for attr, val in (
                    ("externalStorageRoot", externalStorageRoot),
                    ("appStorageRoot", appStorageRoot),
                )
            ):
                Logger.info(
                    f"{type(cls).__name__}: _get_mindref_utils_cls - Recreating MindRefUtils - Parameters Changed"
                )
                cls._utils_cls = None
                cls._mindref_callback_java = None
                return cls._get_mindref_utils_cls(
                    externalStorageRoot, appStorageRoot, context
                )
            return cls._utils_cls

    @classmethod
    def _get_activity(cls) -> "ActivityProtocol":
        return autoclass(ACTIVITY_CLASS_NAME).mActivity

    @classmethod
    def _get_context(cls, activity: "ActivityProtocol"):
        return activity.getContext()

    @classmethod
    def _get_resolver(cls, activity: "ActivityProtocol") -> "ContentResolverProtocol":
        return activity.getContentResolver()

    @staticmethod
    def _inject_activity_code(activity_code: int):
        """Adds an activity code to callback"""

        def dec_inject(func: Callable[Concatenate[int, P], F]) -> Callable[P, F]:
            @wraps(func)
            def wrapped_inject(*args: P.args, **kwargs: P.kwargs) -> F:
                return func(activity_code, *args, **kwargs)

            return wrapped_inject

        return dec_inject

    """
    Register Java Callbacks
    """

    @classmethod
    def _register_prompt_folder_callback(cls, activity_code):
        """Register a Java native on_complete with our Java Activity that in turn calls our python on_complete and then
        finally calls user python callbacks

        Parameters
        ----------
        activity_code
        """

        cls._prompt_folder_callback_java = OnDocumentCallback(
            py_mediator=cls._get_mediator, activity_code=activity_code
        )
        activity = cls._get_activity()
        activity.registerActivityResultListener(cls._prompt_folder_callback_java)

    @classmethod
    def _get_mediator(cls):
        return cls._mindref_callback_py_mediator

    @classmethod
    def _register_mindref_utils_callback(cls, instance):
        """
        Register a Java native interface to call cls._mindref_callback_py_mediator
        """
        cls._mindref_callback_java = MindRefUtilsCallback(cls._get_mediator)
        instance.setMindRefCallback(cls._mindref_callback_java)

    @classmethod
    def _take_persistable_permission(cls, uri: str | UriProtocol) -> str | UriProtocol:
        """After user selects DocumentTree, we want to persist the permission"""
        Intent: "IntentProtocol" = autoclass("android.content.Intent")
        pyActivity: "ActivityProtocol" = cls._get_activity()
        resolver: "ContentResolverProtocol" = cls._get_resolver(pyActivity)
        uri_native: UriProtocol = cls.ensure_uri_type(uri, UriProtocol)
        resolver.takePersistableUriPermission(
            uri_native,
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
        )
        return uri

    @classmethod
    def _python_picker_callback(cls, uri: str | UriProtocol):
        """
        Wraps a call from OnDocumentCallback. Ensures we make permission persistable
        Parameters
        ----------
        uri : UriProtocol
        Notes
        -------

        Called from OnDocumentCallback.onActivityResult
        """
        cls._take_persistable_permission(uri)
        if cb := cls._prompt_folder_callback:
            cb(uri)

    @classmethod
    def _python_copy_storage_callback(cls, result: bool):
        if (cb := cls._callbacks[cls.COPY_TO_APP_STORAGE]) and callable(cb):
            Logger.debug(
                f"{cls.__class__.__name__} : copy_storage_callback invoking registered on_complete"
            )
            cb(result)
        else:
            Logger.debug(
                f"{cls.__class__.__name__} : copy_storage_callback no registered callbacks"
            )

    @classmethod
    def _python_get_categories_callback(cls, results: list[str]):
        if (cb := cls._callbacks[cls.GET_NOTE_CATEGORIES]) and callable(cb):
            Logger.debug(
                f"{cls.__class__.__name__} : get_categories - invoking registered on_complete"
            )
            cb(results)
        else:
            Logger.debug(
                f"{cls.__class__.__name__} : get_categories - no registered on_complete"
            )

    @classmethod
    def _python_manage_categories_callback(cls, category: str, result: bool):
        if (cb := cls._callbacks[cls.MANAGE_CATEGORIES]) and callable(cb):
            Logger.debug(
                f"{cls.__class__.__name__} : manage_categories - invoking registered on_complete"
            )
            cb(category, result)
        else:
            Logger.debug(
                f"{cls.__class__.__name__} : get_categories - no registered on_complete"
            )

    @classmethod
    def ensure_uri_type(
        cls, uri: str | UriProtocol, target: Type[str] | Type[UriProtocol]
    ):
        match (uri, target):
            case str(), str():
                Logger.debug(f"URI is str, target is str")
                return uri
            case str(), x if x is UriProtocol:
                Logger.debug(f"URI is str, target is URI")
                URI: UriProtocol = autoclass("android.net.Uri")
                uri_native = URI.parse(uri)
                return uri_native
            case UriProtocol(), str():
                Logger.debug(f"URI is URI, target is str")
                return uri.toString()
            case UriProtocol(), x if x is UriProtocol:
                Logger.debug(f"URI is URI, target is URI")
                return uri
            case _:
                Logger.debug("Unmatched")

    @classmethod
    def prompt_for_external_folder(cls, activity_code: int):
        """
        Use Android System Document Picker to have user select a folder as a root directory for App Data

        Parameters
        ----------
        activity_code : int
            Arbitrary int, that will be passed to py_mediator

        Notes
        ------
        This will suspend the App while Android Native picker is shown
        """
        with cls._lock:
            if not cls._prompt_folder_callback_java:
                cls._register_prompt_folder_callback(activity_code)
            activity = cls._get_activity()
            Intent = autoclass("android.content.Intent")
            intent = Intent()
            intent.setAction(Intent.ACTION_OPEN_DOCUMENT_TREE)
        activity.startActivityForResult(intent, 1)

    @classmethod
    def get_categories(cls, source: str, target: str | Path, key: int):

        target = str(target)
        with cls._lock:
            activity = cls._get_activity()
            context: "ContextProtocol" = cls._get_context(activity)
            mrUtils = cls._get_mindref_utils_cls(source, target, context)
            if not cls._mindref_callback_java:
                cls._register_mindref_utils_callback(mrUtils)
        mrUtils.getNoteCategories(key)
        Logger.info(f"{type(cls).__name__}: get_categories - invoked")

    @classmethod
    def clone_external_storage(cls, source: str, target: str | Path, key: int):
        """Copy externalStorage to target directory with Android"""
        target = str(target)
        with cls._lock:
            activity = cls._get_activity()
            context: "ContextProtocol" = cls._get_context(activity)
            mrUtils = cls._get_mindref_utils_cls(source, target, context)
            if not cls._mindref_callback_java:
                cls._register_mindref_utils_callback(mrUtils)
        mrUtils.copyToAppStorage(key)

    @classmethod
    def copy_to_external_storage(
        cls,
        filePath: str | Path,
        appStorageRoot: str,
        externalStorageRoot: str,
        key: int,
    ):
        """Persist a file to external storage on Android"""
        with cls._lock:
            activity = cls._get_activity()
            context = cls._get_context(activity)
            mrUtils = cls._get_mindref_utils_cls(
                externalStorageRoot, appStorageRoot, context
            )
            if not cls._mindref_callback_java:
                cls._register_mindref_utils_callback(mrUtils)

        source = Path(filePath)
        source_ext = source.suffix
        match source_ext:
            case ".md":
                source_mime = "text/markdown"
            case ".png":
                source_mime = "image/png"
            case _:
                Logger.error(f"Unknown mime type from source extension: {source_ext}")
                source_mime = ""
        mrUtils.copyToExternalStorage(
            key, str(source), source.parent.stem, source.stem, source_mime
        )
