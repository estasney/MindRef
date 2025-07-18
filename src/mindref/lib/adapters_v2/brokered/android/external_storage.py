from collections.abc import Callable
from threading import Lock
from typing import TYPE_CHECKING

from jnius import PythonJavaClass, autoclass, java_method

from . import UriProtocol, get_intent_cls, get_kivy_activity

if TYPE_CHECKING:
    from mindref.lib.adapters.notes.android.interface import ActivityResultCode

ACTIVITY_CLASS_NAMESPACE = "org/kivy/android/PythonActivity"


def KivyActivity():
    return autoclass("org.kivy.android.PythonActivity").mActivity


def ensure_uri_class(uri: str | UriProtocol) -> UriProtocol:
    match uri:
        case UriProtocol():
            return uri
        case str():
            URI = autoclass("android.net.Uri")
            return URI.parse(uri)
        case _:
            raise TypeError(f"Expected UriProtocol or str, got {type(uri)}")


def take_persistable_permission(uri: str | UriProtocol):
    """After user selects and confirms external storage, persist that permission"""
    Intent = autoclass("android.content.Intent")
    pyActivity = autoclass("org.kivy.android.PythonActivity").mActivity
    contentResolver = pyActivity.getContentResolver()

    parsed_uri = ensure_uri_class(uri)
    contentResolver.takePeristableUriPermission(
        parsed_uri,
        Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
    )


class OnDocumentCallback(PythonJavaClass):
    """PythonActivity (Kivy Built-in) calls this after User has selected folder or file with Android Document Picker"""

    __javainterfaces__ = f"{ACTIVITY_CLASS_NAMESPACE}$ActivityResultListener"
    __javacontext__ = "app"

    def __init__(self, py_callback: Callable[[str], None]):
        """

        Parameters
        ----------
        py_callback
            Python code that will receive the op_code, external storage URI
        """
        super().__init__()
        self.py_callback = py_callback
        self.activity_code = 1

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(
        self, requestCode: int, resultCode: "ActivityResultCode", result_data
    ):
        uri: UriProtocol = result_data.getData()
        take_persistable_permission(uri)
        self.py_callback(uri.toString())


class ExternalStorageMixin:
    def __init__(self):
        self.java_on_document_callback = None
        self.kivy_activity = None
        self.jni_lock = Lock()

    def register_external_storage_callback(self, on_complete: Callable[[str], None]):
        with self.jni_lock:
            self.java_on_document_callback = OnDocumentCallback(on_complete)
            self.kivy_activity = get_kivy_activity()
            self.kivy_activity.registerActivityResultListener(
                self.java_on_document_callback
            )

    def unregister_external_storage_callback(self):
        with self.jni_lock:
            if self.java_on_document_callback and self.kivy_activity:
                self.kivy_activity.unregisterActivityResultListener(
                    self.java_on_document_callback
                )
                self.java_on_document_callback = None
                self.kivy_activity = None

    def has_registered_callback(self) -> bool:
        return (
            self.java_on_document_callback is not None
            and self.kivy_activity is not None
        )

    def prompt_for_external_storage(self, on_complete: Callable[[str], None]):
        """
        Prompt the user to select a folder or file in external storage.

        Parameters
        ----------
        on_complete
            Callback function that will be called with the selected URI as a string.
        """
        self.java_on_document_callback = OnDocumentCallback(on_complete)

        if not self.has_registered_callback():
            self.register_external_storage_callback(on_complete)

        Intent = get_intent_cls()
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
        self.kivy_activity.startActivityForResult(intent, 1)
