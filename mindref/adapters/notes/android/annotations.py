from enum import IntEnum
from typing import (
    Any,
    Callable,
    Literal,
    NewType,
    Protocol,
    TYPE_CHECKING,
    runtime_checkable,
)

if TYPE_CHECKING:
    from adapters.notes.android.interface import OnDocumentCallback

ACTIVITY_CLASS_NAME = "org.kivy.android.PythonActivity"
ACTIVITY_CLASS_NAMESPACE = "org/kivy/android/PythonActivity"
MINDREF_CLASS_NAME = "org.estasney.android.MindRefUtils"
MINDREF_CLASS_NAMESPACE = "org/estasney/android/MindRefUtils"
LIntentFlags = Literal[1, 2]

MIME_TYPE = NewType("MIME_TYPE", str)
DISPLAY_NAME_TYPE = NewType("DISPLAY_NAME_TYPE", str)


class ActivityResultCode(IntEnum):
    RESULT_OK = -1
    RESULT_CANCELLED = 0
    RESULT_FIRST_USER = 1


class IntentProtocol(Protocol):
    FLAG_GRANT_READ_URI_PERMISSION: Literal[1]
    FLAG_GRANT_WRITE_URI_PERMISSION: Literal[2]
    data: Any
    getData: Callable


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


# noinspection PyUnusedLocal
class AutoCloseInputStreamProtocol(Protocol):
    def __init__(self, pfd: "ParcelFileDescriptorProtocol"):
        ...

    close: Callable[[], None]
    read: Callable[[], int]


class ParcelFileDescriptorProtocol(Protocol):
    getFileDescriptor: Callable[[], FileDescriptorProtocol]
    close: Callable[[], None]


class ContentResolverProtocol(Protocol):
    takePersistableUriPermission: Callable[[UriProtocol, LIntentFlags], None]
    getType: Callable[[UriProtocol], str]
    openFile: Callable[[UriProtocol, str, None], ParcelFileDescriptorProtocol]


class ContextProtocol(Protocol):
    getContentResolver: Callable[[ContentResolverProtocol], None]


class ApplicationProtocol(Protocol):
    ...


class ActivityProtocol(Protocol):
    mActivity: "ActivityProtocol"
    getContentResolver: Callable[[], ContentResolverProtocol]
    getApplication: Callable[[], ApplicationProtocol]
    getContext: Callable[[], ContextProtocol]
    getAppRoot: Callable[[], str]
    registerActivityResultListener: Callable[["OnDocumentCallback"], None]
    startActivityForResult: Callable[[IntentProtocol, int], None]


class MindRefCopyStorageCallbackProtocol(Protocol):
    onCopyStorageResult: Callable[[bool], None]
    onCopyStorageDirectoryResult: Callable[[str], None]


class MindRefGetCategoriesCallbackProtocol(Protocol):
    onComplete: Callable[[list[str]], None]


# noinspection PyUnusedLocal
class MindRefUtilsProtocol(Protocol):
    externalStorageRoot: str
    appStorageRoot: str

    setStorageCallback: Callable[[MindRefCopyStorageCallbackProtocol], None]
    copyToAppStorage: Callable[[], None]
    setGetCategoriesCallback: Callable[[MindRefGetCategoriesCallbackProtocol], None]
    getNoteCategories: Callable[[], None]
    haveGetCategoriesCallback: bool
    haveStorageCallback: bool
    haveWriteDocumentCallback: bool

    def __init__(
        self, externalStorageRoot: str, appStorageRoot: str, context: ContextProtocol
    ):
        ...

    def copyToExternalStorage(
        self, sourcePath: str, category: str, name: str, mimeType: str
    ):
        ...
