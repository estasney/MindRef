from enum import Flag, auto
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    TYPE_CHECKING,
    Literal,
)

from kivy import Logger
from kivy.clock import Clock

from adapters.notes.android.interface import AndroidStorageManager
from adapters.notes.fs.fs_note_repository import (
    FileSystemNoteRepository,
    TGetCategoriesCallback,
)
from domain.events import DiscoverCategoryEvent
from domain.markdown_note import MarkdownNote
from utils import caller, fmt_attrs, get_app

if TYPE_CHECKING:
    from domain.editable import EditableNote
    from domain.protocols import GetApp
    from adapters.notes.android.annotations import (
        MindRefUtilsCallbackPyMediator,
        MIME_TYPE,
    )

CodeNames = Literal[
    "MIRROR",
    "READ",
    "WRITE",
    "REMOVE",
    "CATEGORIES",
    "NOTES",
    "EXTERNAL_STORAGE",
    "APP_STORAGE",
    "FILE",
    "DIRECTORY",
    "PROMPT_EXTERNAL",
    "PROMPT_EXTERNAL_DIRECTORY",
    "PROMPT_EXTERNAL_FILE",
]


class MindRefCallCodes(Flag):
    MIRROR = auto()  # Mirroring a filesystem
    READ = auto()  # Read without writing
    WRITE = auto()  # Creating a resource
    REMOVE = auto()  # Removing a resource
    PROMPT = auto()  # Asked for User Intervention
    CATEGORIES = auto()  # Operating on categories
    NOTES = auto()  # Operating on notes
    EXTERNAL_STORAGE = auto()  # Target of operation is external storage
    APP_STORAGE = auto()  # Target of operation is app storage
    FILE = auto()  # Target of operation is a file
    DIRECTORY = auto()  # Target of operation is a directory
    PROMPT_EXTERNAL = PROMPT | EXTERNAL_STORAGE
    PROMPT_EXTERNAL_DIRECTORY = PROMPT_EXTERNAL | DIRECTORY
    PROMPT_EXTERNAL_FILE = PROMPT_EXTERNAL | FILE

    @staticmethod
    def check_field(x: int, n: int) -> bool:
        return (x & n) != 0

    @classmethod
    def deconstruct_int(cls, val: int) -> tuple[tuple[CodeNames], bool]:
        fields_true = []
        a_val = abs(val)
        n_bits = a_val.bit_count()
        n_found = 0
        # noinspection PyTypeChecker
        members: Iterable[tuple[CodeNames, int]] = (
            (member.name, member.value) for member in cls
        )
        for name, value in members:
            if n_found == n_bits:
                return tuple(fields_true), val >= 0
            if MindRefCallCodes.check_field(val, value):
                fields_true.append(name)
                n_found += 1
        return tuple(fields_true), val >= 0


class AndroidNoteRepository(FileSystemNoteRepository):
    """
    Attributes
    ----------
    _storage_path
        Commonly accessible filepath
    _native_path
        Android content URI
    """

    _storage_path: Optional[Path]
    _native_path: Optional[str]
    _mediator_callbacks: dict[int, Callable]
    py_mediator: "MindRefUtilsCallbackPyMediator"

    def __init__(self, get_app: "GetApp", new_first: bool):
        super().__init__(get_app, new_first)
        self._native_path = None
        self._mediator_callbacks = {}
        AndroidStorageManager._mindref_callback_py_mediator = self.py_mediator

    @property
    def configured(self) -> bool:
        return self._storage_path is not None and self._native_path is not None

    @property
    def storage_path(self):
        return super().storage_path

    @storage_path.setter
    def storage_path(self, value: str):
        """
        Pass the Android Native URI

        Parameters
        ----------
        value : str
            E.g. content://com.android.externalstorage.documents/tree/primary:
        """
        s_native = str(value)
        if self._native_path == s_native:
            return
        Logger.info(f"{type(self).__name__} : set native path :  {s_native}")
        self._native_path = str(value)
        self._storage_path = Path(get_app().user_data_dir) / "notes"
        self._storage_path.mkdir(exist_ok=True, parents=True)
        self.current_category = None
        self.category_files.clear()
        Logger.info(f"{type(self).__name__}: set storage path : {self._storage_path!s}")

    def py_mediator(self, key: int, *args):
        Logger.info(
            f"{type(self).__name__}: py_mediator - Got Key : {key}, Args: {args}"
        )
        if key not in self._mediator_callbacks:
            Logger.info(
                f"{type(self).__name__}: py_mediator - No callback for code {key}"
            )
            return
        cb = self._mediator_callbacks.pop(key)
        cb(*args)

    def _copy_storage(self, on_complete: Callable[[Any], None]):
        Logger.info(
            f"{type(self).__name__} : Invoking AndroidStorageManager to copy_storage from {self._native_path} to {self._storage_path}"
        )

        key = MindRefCallCodes.MIRROR | MindRefCallCodes.EXTERNAL_STORAGE
        self._mediator_callbacks[key.value()] = on_complete
        AndroidStorageManager.clone_external_storage(
            self._native_path, self._storage_path, key.value()
        )

    def discover_categories(self, on_complete: Optional[Callable[[], None]], *args):
        """
        Find Categories, and associated Note Files
        For Each Category, Found, Pushes a DiscoverCategoryEvent.
        This implementation invokes Android Storage Manager, ensuring App Storage reflects External Storage

        Notes
        -----
        Several chained callbacks

        get_external_storage_categories:
            Syncs External Storage to App Storage (Limited to Directories and Images)
        get_categories:
            Read Categories from App Storage, Emits DiscoverCategoryEvent.
        discover_category:
            For each category, create a `CategoryResourceFiles` instance


        get_categories -> copy_storage -> emit NotesDiscoverCategoryEvents
        """

        def after_reflect_external_storage_files(
            categories: Iterable[str], on_complete_inner: Optional[Callable], *_iargs
        ):
            app = self.get_app()
            for category_name in categories:
                category_resource = self.discover_category(
                    category=category_name, on_complete=None
                )
                self.category_files[category_name] = category_resource
                app.registry.push_event(
                    DiscoverCategoryEvent(
                        category=category_name,
                    )
                )
            Logger.info(
                f"{type(self).__name__}: after_get_categories - Found App Storage Categories, Created "
                f"CategoryResourceFiles, Emitted Discovery "
            )
            if on_complete_inner:
                on_complete_inner()

        def after_get_external_storage_categories():
            Logger.info(
                f"{type(self).__name__}:"
                f" after_get_external_storage_categories - External Storage Categories Copied"
            )

            # Reflect Markdown Files

            # Emit App Storage Categories
            emit_app_categories = partial(
                after_reflect_external_storage_files, on_complete_inner=on_complete
            )
            get_categories_with_cb = caller(
                self, "get_categories", on_complete=emit_app_categories
            )

            # Sync Markdown Files
            sync_external = caller(
                self, "_copy_storage", on_complete=get_categories_with_cb
            )

            Clock.schedule_once(sync_external)

        self.category_files.clear()
        # Discover Categories
        reflect_categories = caller(
            self,
            "get_external_storage_categories",
            on_complete=caller(
                self, "_copy_storage", after_get_external_storage_categories
            ),
        )

        Clock.schedule_once(reflect_categories)

    def get_external_storage_categories(
        self, on_complete: TGetCategoriesCallback
    ) -> None:
        """
        Invoke AndroidStorageManager which will ensure App Storage categories reflect External Storage categories.

        Parameters
        ----------
        on_complete
            A callable which should accept a list of categories

        Notes
        -----
        This reflects directories and image files *only*
        """
        Logger.info(
            f"{type(self).__name__}: get_external_storage_categories - {fmt_attrs(self, '_native_path', '_storage_path')}"
        )
        callback_code = MindRefCallCodes.READ | MindRefCallCodes.CATEGORIES
        self._mediator_callbacks[callback_code] = on_complete
        AndroidStorageManager.get_categories(
            self._native_path, self._storage_path, callback_code
        )

    def save_note(self, note: "EditableNote", on_complete):
        Logger.info(f"{type(self).__name__} : Saving Note : {note}")

        key = MindRefCallCodes.WRITE | MindRefCallCodes.NOTES

        def store_to_external(md_note: MarkdownNote):
            Logger.info(
                f"{type(self).__name__} : storing {md_note.title}.md to external storage"
            )
            note_fp = md_note.filepath

            def inject_md():
                on_complete(md_note)

            self._mediator_callbacks[key] = inject_md
            AndroidStorageManager.copy_to_external_storage(
                note_fp, str(self.storage_path), self._native_path, key
            )

        super().save_note(note, store_to_external)

    def prompt_for_external_folder(self, on_complete: Callable[[], None]):
        """
        Wrapper for `AndroidStorageManager.prompt_for_external_folder` that stores a callback and passes appropriate code

        Parameters
        ----------
        on_complete

        Returns
        -------

        """
        code = MindRefCallCodes.PROMPT_EXTERNAL_DIRECTORY.value()
        self._mediator_callbacks[code] = on_complete
        AndroidStorageManager.prompt_for_external_folder(code)

    def prompt_for_external_file(
        self, ext_filter: list[str], on_complete: Callable[[str], None]
    ):
        code = MindRefCallCodes.PROMPT_EXTERNAL_FILE.value()
        self._mediator_callbacks[code] = on_complete

        def get_mime_types(filters: list[str]) -> set[MIME_TYPE]:
            result = set(())
            image_exts = (".jpg", ".jpeg", ".png")
            doc_exts = (".md",)
            img_mime = MIME_TYPE("image/*")
            doc_mime = MIME_TYPE("document/*")
            any_mime = MIME_TYPE("*/*")
            if any(any((ef.endswith(ie) for ie in image_exts)) for ef in filters):
                result.add(img_mime)

            if any(any((ef.endswith(de) for de in doc_exts)) for ef in filters):
                result.add(doc_mime)
            if not result:
                result.add(any_mime)
            return result

        mime_types = get_mime_types(ext_filter)

        AndroidStorageManager.prompt_for_external_file(code, mime_types)
