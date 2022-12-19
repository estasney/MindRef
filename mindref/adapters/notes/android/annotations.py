from typing import (
    Any,
    Callable,
    Literal,
    NewType,
    Protocol,
    TYPE_CHECKING,
    runtime_checkable,
    overload,
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


class IntentProtocol(Protocol):
    FLAG_GRANT_READ_URI_PERMISSION: Literal[1]
    FLAG_GRANT_WRITE_URI_PERMISSION: Literal[2]
    ACTION_OPEN_DOCUMENT_TREE: Any
    ACTION_OPEN_DOCUMENT: Any
    CATEGORY_OPENABLE: str
    EXTRA_MIME_TYPES: list[MIME_TYPE]
    addCategory: Callable[[str], None]
    data: Any
    getData: Callable
    setAction: Callable
    setType: Callable[[MIME_TYPE], None]


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


class AndroidApplicationProtocol(Protocol):
    ...


class ActivityProtocol(Protocol):
    mActivity: "ActivityProtocol"
    getContentResolver: Callable[[], ContentResolverProtocol]
    getApplication: Callable[[], AndroidApplicationProtocol]
    getContext: Callable[[], ContextProtocol]
    getAppRoot: Callable[[], str]
    registerActivityResultListener: Callable[["OnDocumentCallback"], None]
    startActivityForResult: Callable[[IntentProtocol, int], None]


class MindRefUtilsCallback(Protocol):
    onCompleteCreateCategory: Callable[[int, str], None]
    onCompleteGetCategories: Callable[[int, list[str]], None]
    onCompleteCopyStorage: Callable[[int], None]
    onFailure: Callable[[int], None]


class MindRefUtilsCallbackPyMediator(Protocol):
    @overload
    def __call__(self, _key: int, category: str):
        ...

    @overload
    def __call__(self, _key: int, categories: list[str]):
        ...

    @overload
    def __call__(self, _key: int):
        ...

    def __call__(self, _key, *args):
        ...


# noinspection PyUnusedLocal
class MindRefUtilsProtocol(Protocol):
    externalStorageRoot: str
    appStorageRoot: str
    haveMindRefUtilsCallback: bool

    def __init__(
        self, externalStorageRoot: str, appStorageRoot: str, context: ContextProtocol
    ):
        ...

    def setMindRefCallback(self, callback: MindRefUtilsCallback):
        ...

    def getNoteCategories(self, key: int):
        ...

    def copyToAppStorage(self, key: int):
        ...

    def copyToExternalStorage(
        self, key: int, sourcePath: str, category: str, name: str, mimeType: str
    ):
        ...

    def createCategory(self, key: int, category: str):
        ...
