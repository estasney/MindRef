from functools import partial
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock

from adapters.notes.android.interface import AndroidStorageManager
from adapters.notes.fs.fs_note_repository import (
    FileSystemNoteRepository,
    TGetCategoriesCallback,
)
from domain.events import DiscoverCategoryEvent
from domain.markdown_note import MarkdownNote
from utils import caller, ps

if TYPE_CHECKING:
    from domain.editable import EditableNote


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

    def __init__(self, get_app, new_first: bool):
        super().__init__(get_app, new_first)
        self._native_path = None

    def get_external_storage_categories(
        self, on_complete: TGetCategoriesCallback
    ) -> None:
        """
        Invoke AndroidStorageManager which will ensure App Storage categories reflect External Storage categories.

        Parameters
        ----------
        on_complete
            A callable which should accept a list of categories
        """
        Logger.info(
            f"{self.__class__.__name__}: get_external_storage_categories - {ps(self, '_native_path', '_storage_path')}"
        )
        AndroidStorageManager.get_categories(
            self._native_path, self._storage_path, on_complete
        )

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
        Logger.info(f"{self.__class__.__name__} : set native path :  {value}")
        self._native_path = str(value)
        self._storage_path = Path(App.get_running_app().user_data_dir) / "notes"
        self._storage_path.mkdir(exist_ok=True, parents=True)
        Logger.info(
            f"{self.__class__.__name__}: set storage path : {self._storage_path}"
        )

    def _copy_storage(self, callback: Callable[[Any], None]):
        Logger.info(
            f"{self.__class__.__name__} : Invoking AndroidStorageManager to copy_storage from {self._native_path} to {self._storage_path}"
        )

        AndroidStorageManager.clone_external_storage(
            self._native_path, self._storage_path, callback
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

        def after_get_categories(
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
                f"{self.__class__.__name__}: after_get_categories - Found App Storage Categories, Created "
                f"CategoryResourceFiles, Emitted Discovery "
            )
            if on_complete_inner:
                on_complete_inner()

        def after_get_external_storage_categories(_categories: Iterable[str]):
            Logger.info(
                f"{self.__class__.__name__}: after_get_external_storage_categories - External Storage Categories Copied"
            )

            action = partial(after_get_categories, on_complete_inner=on_complete)
            get_categories_with_cb = caller(self, "get_categories", on_complete=action)
            Clock.schedule_once(get_categories_with_cb)

        self.category_files.clear()
        discover_action = caller(
            self,
            "get_external_storage_categories",
            on_complete=after_get_external_storage_categories,
        )
        Clock.schedule_once(discover_action)

    def save_note(self, note: "EditableNote", on_complete):
        Logger.info(f"{self.__class__.__name__} : Saving Note : {note}")

        def store_to_external(md_note: MarkdownNote):
            Logger.info(
                f"{self.__class__.__name__} : storing {md_note.title}.md to external storage"
            )
            note_fp = md_note.filepath
            AndroidStorageManager.copy_to_external_storage(
                note_fp,
                str(self.storage_path),
                self._native_path,
                lambda dt: on_complete(md_note),
            )

        super().save_note(note, store_to_external)
