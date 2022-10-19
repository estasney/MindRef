from functools import partial
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING

from kivy import Logger
from kivy.app import App
from toolz import groupby

from adapters.notes.android.interface import AndroidStorageManager
from adapters.notes.fs.fs_note_repository import FileSystemNoteRepository
from adapters.notes.fs.utils import discover_folder_notes
from domain.events import NotesDiscoverCategoryEvent
from utils import def_cb

if TYPE_CHECKING:
    pass


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
        self._index = None
        self._current_category = None

    def get_categories(self, on_complete: Optional[Callable[[Iterable[str]], None]]):
        if not self.configured:
            Logger.error(f"{self.__class__.__name__} : not configured")
            return
        Logger.info(
            f"{self.__class__.__name__} : get_categories from {self._native_path}"
        )
        src_doc = AndroidStorageManager.get_document_file(self._native_path)
        AndroidStorageManager.get_categories(src_doc, self._storage_path, on_complete)

    @property
    def configured(self) -> bool:
        return self._storage_path is not None and self._native_path is not None

    @property
    def storage_path(self):
        return self._storage_path

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
            f"{self.__class__.__name__} : _copy_storage from {self._native_path}"
        )
        src_doc = AndroidStorageManager.get_document_file(self._native_path)
        AndroidStorageManager.copy_storage(src_doc, self._storage_path, callback)

    def discover_notes(self, on_complete: Optional[Callable[[], None]], *args):
        """
        Find Categories, and associated Note Files
        For Each Category, Found, Pushes a NotesDiscoverCategoryEvent.
        This implementation copies from the Android Storage Manager, before operating as usual

        Notes
        -----
        Several chained callbacks

        get_categories -> copy_storage -> emit NotesDiscoverCategoryEvents
        """

        def discovery_factory(categories: Iterable[str]):
            """Called as on_complete from self.get_categories"""
            Logger.info(f"{self.__class__.__name__} : discovery_factory")

            # We need to call self._copy_storage, but need to bind our categories to a callback first

            def is_md(p: Path):
                return p.suffix == ".md"

            def after_get_categories(result: bool, d_categories):
                # Run after copying to local storage
                # result is not used but is passed from callback
                app_inner = self.get_app()
                for category_name_inner in d_categories:
                    category_folder = Path(self.storage_path) / category_name_inner
                    category_files = list(
                        discover_folder_notes(category_folder, new_first=self.new_first)
                    )

                    category_files = groupby(is_md, category_files)
                    category_note_files = category_files.get(True, [])
                    if category_img_inner := category_files.get(False):
                        category_img_inner = category_img_inner[0]

                    self._category_files[category_name_inner] = category_note_files
                    self._category_imgs[category_name_inner] = category_img_inner
                    app_inner.registry.push_event(
                        NotesDiscoverCategoryEvent(
                            category=category_name_inner,
                            image_path=category_img_inner,
                            notes=category_note_files,
                        )
                    )

            proc_categories = partial(after_get_categories, d_categories=categories)
            app = self.get_app()
            # We can display the categories as we have name and image
            for category_name in categories:
                Logger.info(f"Early Process Category {category_name}")
                Logger.info(f"Image? {self.storage_path / category_name}")
                category_path = self.storage_path / category_name
                category_img = next(category_path.glob("*.png"))
                category_notes = Path(self.storage_path, category_name).glob("*.md")
                self._category_files[category_name] = list(category_notes)
                self._category_imgs[category_name] = category_img

                # The list of notes will soon be updated as part of another callback soon after
                app.registry.push_event(
                    NotesDiscoverCategoryEvent(
                        category=category_name,
                        image_path=category_img,
                        notes=self._category_files[category_name],
                    )
                )
            self._copy_storage(proc_categories)

        if on_complete:
            post_get_cat = def_cb(discovery_factory, on_complete)
        else:
            post_get_cat = discovery_factory
        self.get_categories(post_get_cat)
