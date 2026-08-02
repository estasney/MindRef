from collections.abc import Callable
from enum import IntEnum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NewType,
    Protocol,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    from mindref.lib.adapters.brokered.android.external_storage import (
        OnDocumentCallback,
    )

LIntentFlags = Literal[1, 2, 64, 128]

MIME_TYPE = NewType("MIME_TYPE", str)


class V2MindRefCallCodes(IntEnum):
    PROMPT_EXTERNAL_STORAGE = auto()
    IMPORT_EXTERNAL_STORAGE = auto()
    COPY_TO_EXTERNAL_STORAGE = auto()


class IntentProtocol(Protocol):
    FLAG_GRANT_READ_URI_PERMISSION: Literal[1]
    FLAG_GRANT_WRITE_URI_PERMISSION: Literal[2]
    FLAG_GRANT_PERSISTABLE_URI_PERMISSION: Literal[64]
    FLAG_GRANT_PREFIX_URI_PERMISSION: Literal[128]

    ACTION_OPEN_DOCUMENT_TREE: Any
    ACTION_OPEN_DOCUMENT: Any
    CATEGORY_OPENABLE: str
    EXTRA_MIME_TYPES: list[MIME_TYPE]
    addCategory: Callable[[str], "IntentProtocol"]
    data: Any
    addFlags: Callable[[LIntentFlags], "IntentProtocol"]
    getData: Callable[[], "UriProtocol"]
    setAction: Callable[[str], "IntentProtocol"]
    setType: Callable[[MIME_TYPE], "IntentProtocol"]


@runtime_checkable
class UriProtocol(Protocol):
    getPath: Callable[[], str]
    getEncodedPath: Callable[[], str]
    isAbsolute: Callable[[], bool]
    getScheme: Callable[[], str]
    getAuthority: Callable[[], str]
    getPathSegments: Callable[[], list[str]]
    getLastPathSegment: Callable[[], str]
    toString: Callable[[], str]
    parse: Callable[[str], "UriProtocol"]


class FileDescriptorProtocol(Protocol):
    # native java, use with FileInput/OutputStream
    ...


class ParcelFileDescriptorProtocol(Protocol):
    getFileDescriptor: Callable[[], FileDescriptorProtocol]
    close: Callable[[], None]


class ContentResolverProtocol(Protocol):
    takePersistableUriPermission: Callable[[UriProtocol, int], None]
    getType: Callable[[UriProtocol], str]
    openFile: Callable[[UriProtocol, str, None], ParcelFileDescriptorProtocol]


class ContextProtocol(Protocol):
    getContentResolver: Callable[[ContentResolverProtocol], None]


class AndroidApplicationProtocol(Protocol): ...


class ActivityProtocol(Protocol):
    mActivity: "ActivityProtocol"
    getContentResolver: Callable[[], ContentResolverProtocol]
    getApplication: Callable[[], AndroidApplicationProtocol]
    getContext: Callable[[], ContextProtocol]
    getAppRoot: Callable[[], str]
    registerActivityResultListener: Callable[["OnDocumentCallback"], None]
    startActivityForResult: Callable[[IntentProtocol, int], None]


class MindRefWindowInsetsProtocol(Protocol):
    applyToContentView: Callable[[ActivityProtocol, int], None]


class MindRefUtilsCallbackProtocol(Protocol):
    onComplete: Callable[[int], None]
    onFailure: Callable[[int], None]


class MindRefUtilsCallbackPyMediator(Protocol):
    @overload
    def __call__(self, _key: int, category: str, /) -> None: ...

    @overload
    def __call__(self, _key: int, categories: list[str], /) -> None: ...

    @overload
    def __call__(self, _key: int, /) -> None: ...


class MindRefUtilsCallbackPyMediatorProvider(Protocol):
    def __call__(self) -> MindRefUtilsCallbackPyMediator: ...


class MindRefUtilsProtocol(Protocol):
    externalStorageRoot: str
    appStorageRoot: str
    haveMindRefUtilsCallback: bool

    def __init__(
        self, externalStorageRoot: str, appStorageRoot: str, context: ContextProtocol
    ) -> None: ...

    def setMindRefCallback(self, callback: MindRefUtilsCallbackProtocol) -> None: ...

    def copyToAppStorage(self, key: int) -> None: ...

    def copyToExternalStorage(
        self, key: int, sourcePath: str, directory: str, name: str, mimeType: str
    ) -> None: ...
