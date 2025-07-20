from collections.abc import Callable
from enum import IntEnum, auto
from threading import Lock
from typing import TYPE_CHECKING

from jnius import PythonJavaClass, autoclass, java_method
from kivy import Logger

from . import UriProtocol, get_intent_cls, get_kivy_activity

if TYPE_CHECKING:
    from mindref.lib.adapters.notes.android.interface import ActivityResultCode

ACTIVITY_CLASS_NAMESPACE = "org/kivy/android/PythonActivity"


class V2MindRefCallCodes(IntEnum):
    PROMPT_EXTERNAL_STORAGE = auto()


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

    __javainterfaces__ = "org/kivy/android/PythonActivity$ActivityResultListener"
    __javacontext__ = "app"

    def __init__(self, py_callback: Callable[[int, ...], None]):
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
    callbacks: dict[int, Callable]

    def __init__(self):
        self.jni_lock = Lock()
        self.java_on_document_callback = None
        self.kivy_activity = None
        self.callbacks = {}

    def callback_manager(self, key: int, *args):
        """
        Any `PythonJavaClass` that we register uses this as a callback - this prevents multiple registrations
        """

        Logger.info(
            f"{type(self).__name__}: py_mediator - Got Key : {key}, Args: {args}"
        )
        if key not in self.callbacks:
            Logger.info(
                f"{type(self).__name__}: py_mediator - No callback for code {key}"
            )
            return
        callback = self.callbacks.pop(key)
        callback(*args)

    def register_external_storage_callback(self):
        Logger.info(
            f"{type(self).__name__}: Registering external storage callback - attempting to get lock"
        )
        with self.jni_lock:
            Logger.info(
                f"{type(self).__name__}: Got lock, registering external storage callback"
            )
            self.java_on_document_callback = OnDocumentCallback(self.callback_manager)
            self.kivy_activity = get_kivy_activity()
            self.kivy_activity.registerActivityResultListener(
                self.java_on_document_callback
            )

    def prompt_for_external_storage(self, on_complete: Callable[[str], None]):
        """
        Prompt the user to select a folder or file in external storage.

        Parameters
        ----------
        on_complete
            Callback function that will be called with the selected URI as a string.
        """

        if not self.java_on_document_callback:
            self.register_external_storage_callback()

        key = V2MindRefCallCodes.PROMPT_EXTERNAL_STORAGE.value

        # We actually want to wrap the callback in another, taking the persistable permission
        def wrapped_on_complete(uri: str):
            take_persistable_permission(uri)
            on_complete(uri)

        self.callbacks[key] = wrapped_on_complete

        Intent = get_intent_cls()
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
        self.kivy_activity.startActivityForResult(intent, key)
