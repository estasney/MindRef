import threading
from pathlib import Path
from typing import Callable, Optional, Type

from jnius import PythonJavaClass, autoclass, java_method
from kivy import Logger

from adapters.notes.android.annotations import (
    ACTIVITY_CLASS_NAME,
    ACTIVITY_CLASS_NAMESPACE,
    ActivityProtocol,
    ActivityResultCode,
    ContentResolverProtocol,
    DocumentProtocol,
    IntentProtocol,
    MINDREF_CLASS_NAME,
    MINDREF_CLASS_NAMESPACE,
    MindRefUtilsProtocol,
    UriProtocol,
)


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
        # uri.toString() - content://com.android.externalstorage.documents/tree/primary%3Amindref_notes
        # uri.getPath() - /tree/primary:mindref_notes
        # tree_uri looks like content://tree...
        # ontent://com.android.externalstorage.documents/tree/primary%3Amindref_notes - /tree/primary:mindref_notes
        # we can't use this as a path and have to go through Storage Access Framework
        tree_uri: UriProtocol = result_data.getData()
        Logger.debug(
            f"OnDocumentCallback: Selected uri - {tree_uri.toString()} - {tree_uri.getPath()}"
        )
        return self.callback(tree_uri.toString())


class AndroidStorageManager:
    OPEN_DOCUMENT_TREE = 1
    COPY_STORAGE = 2
    GET_CATEGORIES = 3
    _java_mindref_utils_cls: Optional[MindRefUtilsProtocol] = None
    _java_cb_open_document_tree = None
    _java_cb_copy_storage = None
    _java_cb_get_categories = None
    _lock = threading.Lock()
    _callbacks: dict[int, Callable] = {
        OPEN_DOCUMENT_TREE: None,
        COPY_STORAGE: None,
        GET_CATEGORIES: None,
    }

    @classmethod
    def _get_mindref_utils_cls(cls) -> MindRefUtilsProtocol:
        if cls._java_mindref_utils_cls is not None:
            return cls._java_mindref_utils_cls

        mrUtils: MindRefUtilsProtocol = autoclass(MINDREF_CLASS_NAME)()
        cls._java_mindref_utils_cls = mrUtils
        return cls._java_mindref_utils_cls

    @classmethod
    def _get_activity(cls) -> ActivityProtocol:
        return autoclass(ACTIVITY_CLASS_NAME).mActivity

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
    def _register_copy_storage_callback(cls):
        """Register a Java native on_complete with MindRefUtils that in turn calls our python on_complete and then finally
        calls user python callbacks"""
        cls._java_cb_copy_storage = OnCopyAppStorageCallback(
            cls._python_copy_storage_callback
        )

        mrUtils = cls._get_mindref_utils_cls()
        mrUtils.setStorageCallback(cls._java_cb_copy_storage)

    @classmethod
    def _register_get_categories_callback(cls):
        """Register a Java native on_complete with MindRefUtils that in turn calls our python on_complete and then finally
        calls user python callbacks"""
        cls._java_cb_get_categories = GetCategoriesCallback(
            cls._python_get_categories_callback
        )

        mrUtils = cls._get_mindref_utils_cls()
        mrUtils.setGetCategoriesCallback(cls._java_cb_get_categories)

    @classmethod
    def _take_persistable_permission(cls, uri: str | UriProtocol):
        """After user selects DocumentTree, we want to persist the permission"""
        Intent: IntentProtocol = autoclass("android.content.Intent")
        pyActivity: ActivityProtocol = cls._get_activity()
        resolver: ContentResolverProtocol = cls._get_resolver(pyActivity)
        uri_native: UriProtocol = cls._ensure_uri_type(uri, UriProtocol)
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
    def _ensure_uri_type(
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
    def get_document_file(cls, uri: str | UriProtocol) -> DocumentProtocol:
        """
        Get a DocumentFile class, given uri. Required for usage with `cls.copy_storage`
        """
        DocumentFile: DocumentProtocol = autoclass(
            "androidx.documentfile.provider.DocumentFile"
        )
        activity = cls._get_activity()
        app = activity.getApplication()
        uri_native: UriProtocol = cls._ensure_uri_type(uri, UriProtocol)
        return DocumentFile.fromTreeUri(app, uri_native)

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
        source: DocumentProtocol,
        target: str | Path,
        callback: Callable[[list[str]], None],
    ):
        cls._callbacks[cls.GET_CATEGORIES] = callback
        with cls._lock:
            if not cls._java_cb_get_categories:
                cls._register_get_categories_callback()
            activity = cls._get_activity()
            content_resolver: ContentResolverProtocol = cls._get_resolver(activity)
            mrUtils = cls._get_mindref_utils_cls()
        mrUtils.getNoteCategories(source, str(target), content_resolver)

    @classmethod
    def copy_storage(
        cls,
        source: DocumentProtocol,
        target: str | Path,
        callback: Callable[[bool], None],
    ):
        """Copy source directory to target directory with Android"""
        cls._callbacks[cls.COPY_STORAGE] = callback
        with cls._lock:
            if not cls._java_cb_copy_storage:
                cls._register_copy_storage_callback()
            activity = cls._get_activity()
            content_resolver: ContentResolverProtocol = cls._get_resolver(activity)
            mrUtils = cls._get_mindref_utils_cls()
        mrUtils.copyToAppStorage(source, str(target), content_resolver)

    @classmethod
    def to_native_uri(cls, uri: str) -> UriProtocol:
        return cls._ensure_uri_type(uri, UriProtocol)
