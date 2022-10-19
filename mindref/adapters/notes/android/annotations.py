from enum import IntEnum
from typing import (
    Any,
    Callable,
    Literal,
    NewType,
    Optional,
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


class ApplicationProtocol(Protocol):
    ...


class ContextProtocol(Protocol):
    ...


class ActivityProtocol(Protocol):
    mActivity: "ActivityProtocol"
    getContentResolver: Callable[[], ContentResolverProtocol]
    getApplication: Callable[[], ApplicationProtocol]
    getContext: Callable[[], ContextProtocol]
    getAppRoot: Callable[[], str]
    registerActivityResultListener: Callable[["OnDocumentCallback"], None]
    startActivityForResult: Callable[[IntentProtocol, int], None]


class DocumentProtocol(Protocol):
    canRead: Callable[[], bool]
    canWrite: Callable[[], bool]
    createDirectory: Callable[[DISPLAY_NAME_TYPE], "DocumentProtocol"]
    createFile: Callable[[MIME_TYPE, DISPLAY_NAME_TYPE], Optional["DocumentProtocol"]]
    delete: Callable[[], bool]
    exists: Callable[[], bool]
    findFile: Callable[[DISPLAY_NAME_TYPE], Optional["DocumentProtocol"]]
    fromSingleUri: Callable[[ContextProtocol, UriProtocol], "DocumentProtocol"]
    fromTreeUri: Callable[[ApplicationProtocol, UriProtocol], "DocumentProtocol"]
    getName: Callable[[], DISPLAY_NAME_TYPE]
    getParentFile: Callable[[], Optional["DocumentProtocol"]]
    getType: Callable[[], Optional[MIME_TYPE]]
    getUri: Callable[[], UriProtocol]
    isDirectory: Callable[[], bool]
    lastModified: Callable[[], int]
    length: Callable[[], int]
    listFiles: Callable[[], list["DocumentProtocol"]]


class MindRefCopyStorageCallbackProtocol(Protocol):
    onCopyStorageResult: Callable[[bool], None]
    onCopyStorageDirectoryResult: Callable[[str], None]


class MindRefGetCategoriesCallbackProtocol(Protocol):
    onComplete: Callable[[list[str]], None]


class MindRefUtilsProtocol(Protocol):
    setStorageCallback: Callable[[MindRefCopyStorageCallbackProtocol], None]
    copyToAppStorage: Callable[[DocumentProtocol, str, ContentResolverProtocol], None]
    setGetCategoriesCallback: Callable[[MindRefGetCategoriesCallbackProtocol], None]
    getNoteCategories: Callable[[DocumentProtocol, str, ContentResolverProtocol], None]
    haveGetCategoriesCallback: bool
    haveStorageCallback: bool
