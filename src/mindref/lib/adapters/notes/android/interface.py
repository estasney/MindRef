import operator
import threading
from collections.abc import Callable
from enum import IntEnum
from functools import wraps
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Concatenate,
    Optional,
    ParamSpec,
    TypeVar,
)

from jnius import PythonJavaClass, autoclass, java_method
from kivy import Logger
from kivy.clock import Clock

from mindref.lib.adapters.notes.android.annotations import (
    ACTIVITY_CLASS_NAME,
    ACTIVITY_CLASS_NAMESPACE,
    MIME_TYPE,
    MINDREF_CLASS_NAME,
    MINDREF_CLASS_NAMESPACE,
    UriProtocol,
)
from mindref.lib.utils import schedulable

if TYPE_CHECKING:
    from .annotations import (
        ActivityProtocol,
        ContentResolverProtocol,
        ContextProtocol,
        IntentProtocol,
        MindRefUtilsCallbackPyMediator,
        MindRefUtilsProtocol,
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
        mediator = self.py_mediator()
        sched_mediator = schedulable(mediator, key, category)
        Clock.schedule_once(sched_mediator)

    @java_method("(I[Ljava/lang/String;)V", name="onComplete")
    def onCompleteGetCategories(self, key: int, categories: list[str]):
        mediator = self.py_mediator()
        sched_mediator = schedulable(mediator, key, categories)
        Clock.schedule_once(sched_mediator)

    @java_method("(I)V", name="onComplete")
    def onCompleteCopyStorage(self, key: int):
        mediator = self.py_mediator()
        sched_mediator = schedulable(mediator, key)
        Clock.schedule_once(sched_mediator)

    @java_method("(I)V")
    def onFailure(self, key: int):
        # Indicate a failure by making negating the key
        mediator = self.py_mediator()
        sched_mediator = schedulable(mediator, -key)
        Clock.schedule_once(sched_mediator)


class ActivityResultCode(IntEnum):
    RESULT_OK = -1
    RESULT_CANCELLED = 0
    RESULT_FIRST_USER = 1


# noinspection PyPep8Naming,PyUnusedLocal
class OnDocumentCallback(PythonJavaClass):
    """PythonActivity (Kivy Built-in) calls this after User has selected folder or file with Android Document Picker"""

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + "$ActivityResultListener"]
    __javacontext__ = "app"

    def __init__(
        self,
        py_mediator: Callable[[], "MindRefUtilsCallbackPyMediator"],
    ):
        """

        Parameters
        ----------
        py_mediator

            Since result comes from PythonActivity, we can't have to inject the activity code here
        """
        super().__init__()
        self.py_mediator = py_mediator
        self.activity_code = 1

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(
        self, requestCode: int, resultCode: "ActivityResultCode", result_data
    ):
        uri: UriProtocol = result_data.getData()
        Logger.debug(
            f"OnDocumentCallback: Selected uri - {uri.toString()} - {uri.getPath()}"
        )
        mediator = self.py_mediator()
        sched_mediator = schedulable(mediator, requestCode, uri.toString())
        Clock.schedule_once(sched_mediator)
        AndroidStorageManager.take_persistable_permission(uri)


P = ParamSpec("P")
F = TypeVar("F")


# noinspection PyPep8Naming
class AndroidStorageManager:
    _lock = threading.Lock()
    _utils_cls_static: type["MindRefUtilsProtocol"] | None = None
    _utils_cls: Optional["MindRefUtilsProtocol"] = None
    _prompt_picker_callback: Callable[[str], None] | None = None
    _prompt_picker_callback_java: Optional["OnDocumentCallback"] = None
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
    _prompt_picker_callback
        Python callback for prompt_for_folder 
    _prompt_picker_callback_java
        Java callback which call _prompt_picker_callback
    _mindref_callback_java
        MindRefUtilsCallback
    _mindref_callback_py_mediator
        This flexible callable will be responsible for handling variety of parameters from Java side.
    """

    @classmethod
    def _get_mindref_utils_static_cls(cls) -> type["MindRefUtilsProtocol"]:
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
    def _register_prompt_picker_callback(cls):
        """Register a Java native on_complete with our Java Activity that in turn calls our python on_complete and then
        finally calls user python callbacks

        """

        cls._prompt_picker_callback_java = OnDocumentCallback(cls._get_mediator)
        activity = cls._get_activity()
        activity.registerActivityResultListener(cls._prompt_picker_callback_java)

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
    def take_persistable_permission(cls, uri: str | UriProtocol) -> str | UriProtocol:
        """After user selects DocumentTree, we want to persist the permission"""
        Intent: IntentProtocol = autoclass("android.content.Intent")
        pyActivity: ActivityProtocol = cls._get_activity()
        resolver: ContentResolverProtocol = cls._get_resolver(pyActivity)
        uri_native: UriProtocol = cls.ensure_uri_type(uri, UriProtocol)
        resolver.takePersistableUriPermission(
            uri_native,
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
        )
        Logger.info(f"{type(cls).__name__}: take_persistable_permission - {uri}")
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
        cls.take_persistable_permission(uri)
        if cb := cls._prompt_picker_callback:
            cb(uri)

    @classmethod
    def ensure_uri_type(
        cls, uri: str | UriProtocol, target: type[str] | type[UriProtocol]
    ):
        match (uri, target):
            case str(), str():
                Logger.debug("URI is str, target is str")
                return uri
            case str(), x if x is UriProtocol:
                Logger.debug("URI is str, target is URI")
                URI: UriProtocol = autoclass("android.net.Uri")
                uri_native = URI.parse(uri)
                return uri_native
            case UriProtocol(), str():
                Logger.debug("URI is URI, target is str")
                return uri.toString()
            case UriProtocol(), x if x is UriProtocol:
                Logger.debug("URI is URI, target is URI")
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
            if not cls._prompt_picker_callback_java:
                cls._register_prompt_picker_callback()
            activity = cls._get_activity()
            Intent = autoclass("android.content.Intent")
            intent: IntentProtocol = (
                Intent()
                .setAction(Intent.ACTION_OPEN_DOCUMENT_TREE)
                .addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                .addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                .addFlags(Intent.FLAG_GRANT_PREFIX_URI_PERMISSION)
            )
        activity.startActivityForResult(intent, activity_code)

    @classmethod
    def prompt_for_external_file(cls, activity_code: int, mime_types: set[MIME_TYPE]):
        with cls._lock:
            if not cls._prompt_picker_callback_java:
                cls._register_prompt_picker_callback()
            activity = cls._get_activity()
            Intent: type[IntentProtocol] = autoclass("android.content.Intent")
            intent = (
                Intent()
                .setAction(Intent.ACTION_OPEN_DOCUMENT)
                .addCategory(Intent.CATEGORY_OPENABLE)
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            )

            any_mime = MIME_TYPE("*/*")

            match len(mime_types), any_mime in mime_types:
                case 0, _:
                    intent.setType(any_mime)
                case 1, _:
                    intent.setType(mime_types.pop())
                case int(), True:
                    intent.setType(any_mime)
                    mime_types.remove(any_mime)
                    intent.EXTRA_MIME_TYPES = list(mime_types)
                case int(), False:
                    intent.setType(mime_types.pop())
                    intent.EXTRA_MIME_TYPES = list(mime_types)
        Logger.info(
            f"{type(cls).__name__}: prompt_for_external_file - code {activity_code}"
        )
        activity.startActivityForResult(intent, activity_code)

    @classmethod
    def get_categories(cls, source: str, target: str | Path, key: int):
        target = str(target)
        with cls._lock:
            activity = cls._get_activity()
            context: ContextProtocol = cls._get_context(activity)
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
            context: ContextProtocol = cls._get_context(activity)
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
        source_ext = source.suffix if source.suffix else ""
        match source_ext.lower():
            case ".md":
                source_mime = "text/markdown"
            case ".png" | ".jpg" | ".jpeg" as ext:
                source_mime = f"image/{ext[1:]}"
            case _:
                Logger.error(f"Unhandled mime type from source extension: {source_ext}")
                source_mime = ""
        mrUtils.copyToExternalStorage(
            key, str(source), source.parent.stem, source.stem, source_mime
        )

    @classmethod
    def create_category_directory(
        cls, directoryName: str, appStorageRoot: str, externalStorageRoot: str, key: int
    ):
        """
        Create a directory on external storage on Android

        Parameters
        ----------
        directoryName : str
            Name of directory to create
        appStorageRoot : str
            Path to app storage root
        externalStorageRoot : str
            Path to external storage root (Uri from OPEN_DOCUMENT_TREE)
        key : int
            Arbitrary int, that will be passed to py_mediator when callback is invoked

        """
        with cls._lock:
            activity = cls._get_activity()
            context = cls._get_context(activity)
            mrUtils = cls._get_mindref_utils_cls(
                externalStorageRoot, appStorageRoot, context
            )
            if not cls._mindref_callback_java:
                cls._register_mindref_utils_callback(mrUtils)
        mrUtils.createCategory(key, directoryName)

    @classmethod
    def add_category_image(
        cls,
        directoryName: str,
        appStorageRoot: str,
        externalStorageRoot: str,
        imageUri: str,
        key: int,
    ):
        """
        Add an image to a category directory on external storage on Android.

        Parameters
        ----------
        directoryName : str
            Category name that image will be added to. This should already exist.
        appStorageRoot : str
            Path to app storage root. Used only for caching purposes.
        externalStorageRoot : str
            Path to our managed external storage root (Uri from OPEN_DOCUMENT_TREE)
        imageUri : str
            Content Uri of image to add to category from OPEN_DOCUMENT
        key : int
            Arbitrary int, that will be passed to py_mediator when callback is invoked

        Returns
        -------

        """
        with cls._lock:
            activity = cls._get_activity()
            context = cls._get_context(activity)
            mrUtils = cls._get_mindref_utils_cls(
                externalStorageRoot, appStorageRoot, context
            )
            if not cls._mindref_callback_java:
                cls._register_mindref_utils_callback(mrUtils)
        srcUri = cls.ensure_uri_type(imageUri, UriProtocol)
        Logger.info(
            f"{type(cls).__name__}: add_category_image - [srcUri={imageUri}][dir={directoryName}]"
        )
        mrUtils.copyToManagedExternal(key, srcUri, directoryName)
