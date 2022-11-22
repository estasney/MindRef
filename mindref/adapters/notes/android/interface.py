import operator
import threading
from pathlib import Path
from typing import Any, Callable, Optional, Type, TYPE_CHECKING

from jnius import PythonJavaClass, autoclass, java_method
from kivy import Logger

from adapters.notes.android.annotations import (
    ACTIVITY_CLASS_NAME,
    ACTIVITY_CLASS_NAMESPACE,
    ActivityProtocol,
    ActivityResultCode,
    ContentResolverProtocol,
    ContextProtocol,
    IntentProtocol,
    MINDREF_CLASS_NAME,
    MINDREF_CLASS_NAMESPACE,
    MindRefUtilsProtocol,
    UriProtocol,
)

if TYPE_CHECKING:
    from adapters.notes.fs.fs_note_repository import TGetCategoriesCallback


# noinspection PyPep8Naming
class OnCopyAppStorageCallback(PythonJavaClass):
    """MindRefUtils.java calls this with True if success, False if failed"""

    __javainterfaces__ = [MINDREF_CLASS_NAMESPACE + "$CopyStorageCallback"]
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[bool], None]):
        super().__init__()
        self.callback = callback

    @java_method("(Z)V")
    def onCopyStorageResult(self, result: bool):
        Logger.debug(f"{self.__class__.__name__} : 'onCopyStorageResult - {result}")
        self.callback(result)


# noinspection PyPep8Naming
class GetCategoriesCallback(PythonJavaClass):
    """
    MindRefUtils, find categories (note folders) creates a mirrored directory and copies the image
    """

    __javainterfaces__ = [MINDREF_CLASS_NAMESPACE + "$GetCategoriesCallback"]
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[list[str]], None]):
        super().__init__()
        self.callback = callback

    @java_method("([Ljava/lang/String;)V")
    def onComplete(self, categories: list[str]):
        self.callback(categories)


# noinspection PyPep8Naming,PyUnusedLocal
class OnDocumentCallback(PythonJavaClass):
    """PythonActivity calls this after User has selected folder with Android Document Picker"""

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + "$ActivityResultListener"]
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(
        self, requestCode: int, resultCode: ActivityResultCode, result_data
    ):

        tree_uri: UriProtocol = result_data.getData()
        Logger.debug(
            f"OnDocumentCallback: Selected uri - {tree_uri.toString()} - {tree_uri.getPath()}"
        )
        return self.callback(tree_uri.toString())


# noinspection PyPep8Naming
class WriteDocumentManagerCallback(PythonJavaClass):
    """PythonActivity calls this after we have written to Android Storage"""

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + "$WriteDocumentManagerCallback"]
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[bool], None]):
        super().__init__()
        self.callback = callback

    @java_method("(Z)V")
    def onComplete(self, result: bool):
        Logger.debug(f"{self.__class__.__name__} : 'onComplete - {result}")
        self.callback(result)


class AndroidStorageManager:
    OPEN_DOCUMENT_TREE = 1
    COPY_STORAGE = 2
    GET_CATEGORIES = 3
    _java_cb_open_document_tree = None
    _java_cb_copy_storage = None
    _java_cb_get_categories = None
    _lock = threading.Lock()
    _utils_cls_static: Optional[Type[MindRefUtilsProtocol]] = None
    _utils_cls: Optional[MindRefUtilsProtocol] = None
    _callbacks: dict[int, Callable[[Any], None]] = {
        OPEN_DOCUMENT_TREE: None,
        COPY_STORAGE: None,
        GET_CATEGORIES: None,
    }

    @classmethod
    def _get_mindref_utils_cls(
        cls, externalStorageRoot: str, appStorageRoot: str, context: ContextProtocol
    ) -> MindRefUtilsProtocol:
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
                cls._utils_cls = None
                return cls._get_mindref_utils_cls(
                    externalStorageRoot, appStorageRoot, context
                )
            return cls._utils_cls

    @classmethod
    def _get_mindref_utils_static_cls(cls) -> Type[MindRefUtilsProtocol]:
        if cls._utils_cls_static is None:
            cls._utils_cls_static = autoclass(MINDREF_CLASS_NAME)
        return cls._utils_cls_static

    @classmethod
    def _get_activity(cls) -> ActivityProtocol:
        return autoclass(ACTIVITY_CLASS_NAME).mActivity

    @classmethod
    def _get_context(cls, activity: ActivityProtocol):
        return activity.getContext()

    @classmethod
    def _get_resolver(cls, activity: ActivityProtocol) -> ContentResolverProtocol:
        return activity.getContentResolver()

    @classmethod
    def _register_picker_callback(cls):
        """Register a Java native on_complete with our Java Activity that in turn calls our python on_complete and then
        finally calls user python callbacks"""
        cls._java_cb_open_document_tree = OnDocumentCallback(
            cls._python_picker_callback
        )
        activity = cls._get_activity()
        activity.registerActivityResultListener(cls._java_cb_open_document_tree)

    @classmethod
    def _register_copy_storage_callback(
        cls, source: str, target: str, context: ContextProtocol
    ):
        """Register a Java native on_complete with MindRefUtils that in turn calls our python on_complete and then finally
        calls user python callbacks

        Parameters
        ----------
        source
        target
        context"""
        cls._java_cb_copy_storage = OnCopyAppStorageCallback(
            cls._python_copy_storage_callback
        )

        mrUtils = cls._get_mindref_utils_cls(source, target, context)
        mrUtils.setStorageCallback(cls._java_cb_copy_storage)

    @classmethod
    def _register_get_categories_callback(
        cls, source: str, target: str, context: ContextProtocol
    ):
        """Register a Java native on_complete with MindRefUtils that in turn calls our python on_complete and then finally
        calls user python callbacks

        Parameters
        ----------"""
        cls._java_cb_get_categories = GetCategoriesCallback(
            cls._python_get_categories_callback
        )

        mrUtilsStatic = cls._get_mindref_utils_cls(source, target, context)
        mrUtilsStatic.setGetCategoriesCallback(cls._java_cb_get_categories)

    @classmethod
    def _take_persistable_permission(cls, uri: str | UriProtocol):
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

    @classmethod
    def _python_picker_callback(cls, uri: str | UriProtocol):
        """
        Called directly from OnDocumentCallback
        Parameters
        ----------
        uri : UriProtocol
        Notes
        -------

        Called from OnDocumentCallback.onActivityResult
        """
        cls._take_persistable_permission(uri)
        if (cb := cls._callbacks[cls.OPEN_DOCUMENT_TREE]) and callable(cb):
            cb(uri)

    @classmethod
    def _python_copy_storage_callback(cls, result: bool):
        if (cb := cls._callbacks[cls.COPY_STORAGE]) and callable(cb):
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
        if (cb := cls._callbacks[cls.GET_CATEGORIES]) and callable(cb):
            Logger.debug(
                f"{cls.__class__.__name__} : get_categories - invoking registered on_complete"
            )
            cb(results)
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
    def select_folder(cls, callback: Callable[[str], None]):
        """
        Use Android System Document Picker to have user select a folder

        Parameters
        ----------
        callback : Callable
        """
        cls._callbacks[cls.OPEN_DOCUMENT_TREE] = callback
        with cls._lock:
            if not cls._java_cb_open_document_tree:
                cls._register_picker_callback()
            activity = cls._get_activity()
            Intent = autoclass("android.content.Intent")
            intent = Intent()
            intent.setAction(Intent.ACTION_OPEN_DOCUMENT_TREE)
        activity.startActivityForResult(intent, 1)

    @classmethod
    def get_categories(
        cls,
        source: str,
        target: str | Path,
        callback: "TGetCategoriesCallback",
    ):
        target = str(target)
        cls._callbacks[cls.GET_CATEGORIES] = callback
        with cls._lock:
            activity = cls._get_activity()
            context: ContextProtocol = cls._get_context(activity)
            if not cls._java_cb_get_categories:
                cls._register_get_categories_callback(source, target, context)

            mrUtils = cls._get_mindref_utils_cls(source, target, context)
        mrUtils.getNoteCategories()

    @classmethod
    def clone_external_storage(
        cls,
        source: str,
        target: str | Path,
        callback: Callable[[bool], None],
    ):
        """Copy externalStorage to target directory with Android"""
        target = str(target)
        cls._callbacks[cls.COPY_STORAGE] = callback
        with cls._lock:
            activity = cls._get_activity()
            context: ContextProtocol = cls._get_context(activity)
            if not cls._java_cb_copy_storage:
                cls._register_copy_storage_callback(source, target, context)
            mrUtils = cls._get_mindref_utils_cls(source, target, context)
        mrUtils.copyToAppStorage()

    @classmethod
    def copy_to_external_storage(
        cls,
        filePath: str | Path,
        appStorageRoot: str,
        externalStorageRoot: str,
        callback: Callable[[bool], None],
    ):
        """Persist a file to external storage on Android"""
        cls._callbacks[cls.COPY_STORAGE] = callback
        with cls._lock:
            activity = cls._get_activity()
            context = cls._get_context(activity)
            if not cls._java_cb_copy_storage:
                cls._register_copy_storage_callback(
                    externalStorageRoot, appStorageRoot, context
                )
            mrUtils = cls._get_mindref_utils_cls(
                externalStorageRoot, appStorageRoot, context
            )
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
            str(source), source.parent.stem, source.stem, source_mime
        )
