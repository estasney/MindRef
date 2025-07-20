from collections.abc import Callable
from enum import IntEnum, auto
from typing import Any, ClassVar, Concatenate, Literal, ParamSpec

from jnius import PythonJavaClass, autoclass, java_method
from kivy import Logger

from mindref.lib.adapters.notes.android.annotations import (
    ActivityProtocol,
    ContentResolverProtocol,
    IntentProtocol,
)
from mindref.lib.adapters_v2.brokered.android import UriProtocol
from mindref.lib.utils import Singleton

ACTIVITY_CLASS_NAME = "org.kivy.android.PythonActivity"
ACTIVITY_CLASS_NAMESPACE = "org/kivy/android/PythonActivity"

_kivy_activity: ActivityProtocol = autoclass(ACTIVITY_CLASS_NAME).mActivity


TDocumentResultCode = Literal[-1, 0, 1]
CBArgs = ParamSpec("CBArgs")


class V2MindRefCallCodes(IntEnum):
    PROMPT_EXTERNAL_STORAGE = auto()


TKeyedCallbackInner = Callable[Concatenate[V2MindRefCallCodes, CBArgs], None]
TKeyedCallback = Callable[[], TKeyedCallbackInner]


class OnDocumentCallback(PythonJavaClass):
    """
    PythonActivity (Kivy Built-in) calls this after User has selected folder or file with Android Document Picker

    Notes
    -----
    - This class needs to be registered as an ActivityResultListener in the Kivy Android activity.
    """

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + "$ActivityResultListener"]
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[int, str | UriProtocol], None]) -> None:
        super().__init__()
        self.py_callback = callback
        self.activity_code = 1

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(
        self, requestCode: int, resultCode: TDocumentResultCode, result_data: Any
    ):
        uri: UriProtocol = result_data.getData()
        Logger.info(
            f"OnDocumentCallback: Selected uri - {uri.toString()} - {uri.getPath()}"
        )
        self.py_callback(requestCode, uri.toString())


class AndroidManager(metaclass=Singleton):
    """
    This class is responsible for implementing the `TKeyedCallback` interface, registering `PythonJavaClass` callbacks,
    and maintaining references to these callbacks.

    In practice, it does not implement the `TKeyedCallback` interface directly, but rather provides a way for another class
    to implement it and set it as the `py_mediator` attribute.
    """

    _py_mediator: TKeyedCallback | None = None
    _java_prompt_picker_callback: OnDocumentCallback | None = None

    @classmethod
    def get_py_mediator(cls) -> TKeyedCallbackInner:
        if cls._py_mediator is None:
            raise ValueError("py_mediator is not set.")
        return cls._py_mediator()

    @classmethod
    def set_py_mediator(cls, py_mediator: TKeyedCallback) -> None:
        if cls._py_mediator is not None:
            raise ValueError("py_mediator is already set - cannot overwrite it.")
        cls._py_mediator = py_mediator

    @classmethod
    def register_java_callbacks(cls):
        def wrapped_external_storage_callback(
            request_code: int, uri: str | UriProtocol
        ):
            Logger.info(
                f"AndroidManager: wrapped_callback called with request_code={request_code}, uri={uri}, taking persistable permission"
            )
            cls.take_persistable_permission(uri)
            Logger.info(
                f"AndroidManager: wrapped_callback - calling py_mediator with request_code={request_code}, uri={uri}"
            )
            call_code = V2MindRefCallCodes(request_code)
            Logger.info(
                f"AndroidManager: wrapped_callback - call_code={call_code}, uri={uri}"
            )
            mediator = cls.get_py_mediator()
            Logger.info(f"AndroidManager: wrapped_callback - mediator={mediator}")
            mediator(call_code, uri)

        cls._java_prompt_picker_callback = OnDocumentCallback(
            wrapped_external_storage_callback
        )
        Logger.info("AndroidManager: Created OnDocumentCallback instance")
        # Register the callback with the Kivy activity
        _kivy_activity.registerActivityResultListener(cls._java_prompt_picker_callback)

    @classmethod
    def ensure_is_uri(cls, uri: str | UriProtocol) -> UriProtocol:
        """Check if the given uri is of type UriProtocol"""
        if isinstance(uri, UriProtocol):
            return uri
        URIClass: UriProtocol = autoclass("android.net.Uri")
        parsed: UriProtocol = URIClass.parse(uri)
        return parsed

    @classmethod
    def take_persistable_permission(cls, uri: str | UriProtocol) -> str | UriProtocol:
        """After user selects DocumentTree, we want to persist the permission"""
        Intent: IntentProtocol = autoclass("android.content.Intent")
        resolver: ContentResolverProtocol = _kivy_activity.getContentResolver()
        uri_native: UriProtocol = cls.ensure_is_uri(uri)
        resolver.takePersistableUriPermission(
            uri_native,
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
        )
        Logger.info(f"{type(cls).__name__}: take_persistable_permission - {uri}")
        return uri

    @classmethod
    def prompt_for_external_storage(cls) -> None:
        # In this case we want to wrap the callback so we can take persistable permissions

        if cls._java_prompt_picker_callback is None:
            cls.register_java_callbacks()

        Logger.info("AndroidManager: Prompting for external storage selection")
        Intent = autoclass("android.content.Intent")
        intent: IntentProtocol = (
            Intent()
            .setAction(Intent.ACTION_OPEN_DOCUMENT_TREE)
            .addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            .addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            .addFlags(Intent.FLAG_GRANT_PREFIX_URI_PERMISSION)
        )
        _kivy_activity.startActivityForResult(
            intent, V2MindRefCallCodes.PROMPT_EXTERNAL_STORAGE.value
        )
