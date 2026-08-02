from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from jnius import PythonJavaClass, java_method
from kivy.logger import Logger

from mindref.lib.adapters.brokered.android.intent import get_intent_cls
from mindref.lib.adapters.brokered.android.kivy_activity import get_kivy_activity
from mindref.lib.adapters.brokered.android.mindref_utils import get_mindref_utils_cls
from mindref.lib.adapters.brokered.android.types import (
    ContentResolverProtocol,
    ContextProtocol,
    IntentProtocol,
    MindRefUtilsCallbackPyMediator,
    MindRefUtilsCallbackPyMediatorProvider,
    MindRefUtilsProtocol,
    UriProtocol,
    V2MindRefCallCodes,
)
from mindref.lib.adapters.brokered.android.uri import get_uri_cls
from mindref.lib.utils import Singleton

ACTIVITY_CLASS_NAMESPACE = "org/kivy/android/PythonActivity"

TDocumentResultCode = Literal[-1, 0, 1]


class OnDocumentCallback(PythonJavaClass):
    """
    PythonActivity (Kivy Built-in) calls this after User has selected folder or file with Android Document Picker

    Notes
    -----
    - This class needs to be registered as an ActivityResultListener in the Kivy Android activity.
    """

    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + "$ActivityResultListener"]  # noqa: RUF012
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[int, str], None]) -> None:
        super().__init__()
        self.py_callback = callback
        self.activity_code = 1

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(
        self, requestCode: int, resultCode: TDocumentResultCode, result_data: Any
    ) -> None:
        uri: UriProtocol = result_data.getData()
        Logger.info(
            f"OnDocumentCallback: Selected uri - {uri.toString()} - {uri.getPath()}"
        )
        self.py_callback(requestCode, uri.toString())


class MindRefUtilsCallback(PythonJavaClass):
    __javainterfaces__ = ["org/estasney/android/MindRefUtils" + "$MindRefUtilsCallback"]  # noqa: RUF012
    __javacontext__ = "app"

    def __init__(self, callback: Callable[[int], None]) -> None:
        super().__init__()
        self.py_callback = callback

    @java_method("(I)V")
    def onComplete(self, result_code: int) -> None:
        """Called from Java when external storage is synced"""
        Logger.info(f"MindRefUtilsCallback: Completed with code {result_code}")
        self.py_callback(result_code)

    @java_method("(I)V")
    def onFailure(self, key: int) -> None:
        self.py_callback(key * -1)  # Negative key to indicate failure


class AndroidManager(metaclass=Singleton):
    """
    This class is responsible for implementing the `TKeyedCallback` interface, registering `PythonJavaClass` callbacks,
    and maintaining references to these callbacks.

    In practice, it does not implement the `TKeyedCallback` interface directly, but rather provides a way for another class
    to implement it and set it as the `py_mediator` attribute.
    """

    _py_mediator: MindRefUtilsCallbackPyMediatorProvider | None = None
    _java_prompt_picker_callback: OnDocumentCallback | None = None
    _java_mindref_utils_callback: MindRefUtilsCallback | None = None
    _java_mindref_utils_class: type[MindRefUtilsProtocol] | None = None
    _java_mindref_utils: MindRefUtilsProtocol | None = None

    @classmethod
    def get_py_mediator(cls) -> MindRefUtilsCallbackPyMediator:
        if cls._py_mediator is None:
            raise ValueError("py_mediator is not set.")
        return cls._py_mediator()

    @classmethod
    def set_py_mediator(
        cls, py_mediator: MindRefUtilsCallbackPyMediatorProvider
    ) -> None:
        if cls._py_mediator is not None:
            raise ValueError("py_mediator is already set - cannot overwrite it.")
        cls._py_mediator = py_mediator

    @classmethod
    def _get_mindref_utils(
        cls, externalStorageRoot: str, appStorageRoot: str, context: "ContextProtocol"
    ) -> MindRefUtilsProtocol:
        # Check if our cached instance has the same parameters

        def matches_parameters(
            instance: MindRefUtilsProtocol,
        ) -> bool:
            return (
                instance.externalStorageRoot == externalStorageRoot
                and instance.appStorageRoot == appStorageRoot
            )

        if cls._java_mindref_utils_class is None:
            cls._java_mindref_utils_class = get_mindref_utils_cls()

        if cls._java_mindref_utils is not None and matches_parameters(
            cls._java_mindref_utils
        ):
            return cls._java_mindref_utils

        utils = cls._java_mindref_utils_class(
            externalStorageRoot, appStorageRoot, context
        )
        callback = cls._java_mindref_utils_callback
        if callback is None:
            callback = cls._register_mindref_utils_callback()
        Logger.info(
            f"{cls.__name__} : Setting MindRefUtilsCallback for {utils.externalStorageRoot=}, {utils.appStorageRoot=}"
        )
        utils.setMindRefCallback(callback)

        cls._java_mindref_utils = utils
        return cls._java_mindref_utils

    @classmethod
    def _register_kivy_java_callbacks(cls) -> None:
        def wrapped_external_storage_callback(request_code: int, uri: str) -> None:
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
        get_kivy_activity().registerActivityResultListener(
            cls._java_prompt_picker_callback
        )

    @classmethod
    def _register_mindref_utils_callback(cls) -> "MindRefUtilsCallback":
        def wrapped_mindref_utils_callback(operation_code: int):
            if operation_code < 0:
                Logger.error(
                    f"AndroidManager: wrapped_mindref_utils_callback called with error, {operation_code=}"
                )
            else:
                Logger.info(
                    f"AndroidManager: wrapped_mindref_utils_callback called with {operation_code=}"
                )

            parseable_code = abs(operation_code)
            try:
                _code = V2MindRefCallCodes(parseable_code)
            except ValueError:
                Logger.error(
                    f"AndroidManager: wrapped_mindref_utils_callback - Invalid result_code={operation_code}, cannot parse to V2MindRefCallCodes"
                )
                raise
            cls.get_py_mediator()(operation_code)

        cls._java_mindref_utils_callback = MindRefUtilsCallback(
            wrapped_mindref_utils_callback
        )
        Logger.info("AndroidManager: Created MindRefUtilsCallback instance")
        return cls._java_mindref_utils_callback

    @classmethod
    def register_java_callbacks(cls):
        Logger.info(f"{type(cls).__name__}: Registering Java callbacks")
        cls._register_kivy_java_callbacks()
        cls._register_mindref_utils_callback()

    @classmethod
    def ensure_is_uri(cls, uri: str | UriProtocol) -> UriProtocol:
        """Check if the given uri is of type UriProtocol"""
        if isinstance(uri, UriProtocol):
            return uri
        URIClass: UriProtocol = get_uri_cls()
        parsed: UriProtocol = URIClass.parse(uri)
        return parsed

    @classmethod
    def take_persistable_permission(cls, uri: str | UriProtocol) -> str | UriProtocol:
        """After user selects DocumentTree, we want to persist the permission"""
        Intent = get_intent_cls()
        resolver = get_kivy_activity().getContentResolver()
        uri_native: UriProtocol = cls.ensure_is_uri(uri)
        resolver.takePersistableUriPermission(
            uri_native,
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
        )
        Logger.info(f"{cls.__name__} : take_persistable_permission - {uri}")
        return uri

    @classmethod
    def prompt_for_external_storage(cls) -> None:
        # In this case we want to wrap the callback so we can take persistable permissions

        if cls._java_prompt_picker_callback is None:
            cls.register_java_callbacks()

        Logger.info("AndroidManager: Prompting for external storage selection")
        Intent = get_intent_cls()
        intent: IntentProtocol = (
            Intent()
            .setAction(Intent.ACTION_OPEN_DOCUMENT_TREE)
            .addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            .addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            .addFlags(Intent.FLAG_GRANT_PREFIX_URI_PERMISSION)
        )
        get_kivy_activity().startActivityForResult(
            intent, V2MindRefCallCodes.PROMPT_EXTERNAL_STORAGE.value
        )

    @classmethod
    def import_external_storage(
        cls, externalStorageRoot: str, appStoragePath: str
    ) -> None:
        """
        Import external storage using the MindRefUtils class.

        Parameters
        ----------
        externalStorageRoot : str
            The root path of the external storage.
        appStoragePath : str
            The root path of the app's storage.
        """
        context: ContextProtocol = get_kivy_activity().getContext()
        utils = cls._get_mindref_utils(externalStorageRoot, appStoragePath, context)
        op_key = V2MindRefCallCodes.IMPORT_EXTERNAL_STORAGE.value
        utils.copyToAppStorage(op_key)

    @classmethod
    def copy_to_external_storage(
        cls, externalStoragePath: str, appStoragePath: str, filePath: str
    ) -> None:
        source = Path(filePath)

        source_ext = source.suffix or ""

        mime_types = {
            ".md": "text/markdown",
        }

        source_mime_type = mime_types.get(source_ext, "")

        context: ContextProtocol = get_kivy_activity().getContext()
        utils = cls._get_mindref_utils(externalStoragePath, appStoragePath, context)

        op_key = V2MindRefCallCodes.COPY_TO_EXTERNAL_STORAGE.value
        Logger.info(
            f"{cls.__name__} : Calling MindRefUtils 'copyToExternalStorage' sourcePath={source!s}, directory={source.parent.stem} name={source.stem} mimeType={source_mime_type}"
        )
        utils.copyToExternalStorage(
            op_key, str(source), source.parent.stem, source.stem, source_mime_type
        )
