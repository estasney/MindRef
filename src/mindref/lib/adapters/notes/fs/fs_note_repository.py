from collections.abc import Callable, Iterable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Union

from kivy import Logger

from mindref.lib.adapters.notes.note_repository import (
    AbstractNoteRepository,
)
from mindref.lib.utils import sch_cb, schedulable

if TYPE_CHECKING:
    from os import PathLike

    from mindref.lib.domain.editable import EditableNote
    from mindref.lib.domain.markdown_note import (
        MarkdownNote,
    )
    from mindref.lib.domain.protocols import GetApp

TGetCategoriesCallback = Callable[[Iterable[str]], None]


class FileSystemNoteRepository(AbstractNoteRepository):
    _storage_path: Path | None
    note_files: list[Path]

    def __init__(self, get_app: "GetApp", **kwargs):
        super().__init__(get_app, **kwargs)
        self._storage_path = None
        self.get_app = get_app
        self.note_files = []

    @property
    def configured(self) -> bool:
        return self._storage_path is not None

    @property
    def storage_path(self) -> Path:
        if not self._storage_path:
            raise AttributeError("Storage Path not set")
        return self._storage_path

    @storage_path.setter
    def storage_path(self, path: Union["PathLike", None]):
        self._storage_path = Path(path) if path else None

    def discover_notes(
        self, on_complete: Callable[[list[Path]], None] | None, *args
    ) -> None:
        """
        Recursively scan our storage_path for valid note file paths
        """
        note_files = (f for f in self.storage_path.rglob("**/*.md") if f.is_file())

        # Newest first
        self.note_files = sorted(
            note_files, key=lambda f: f.stat().st_mtime, reverse=True
        )

        if on_complete:
            on_complete(self.note_files)

    def save_note(
        self,
        note: "EditableNote",
        on_complete: Callable[["MarkdownNote"], None] | None,
    ):
        note_is_new = note.md_note is None
        Logger.info(f"{type(self).__name__} : save_note {note}")

    def get_note(self, category: str, idx: int, on_complete) -> "MarkdownNote":
        # TODO IndexError - Show a new note page
        resource = self.category_files[category].get_note_by_idx(idx)
        md_note = resource.get_note()
        if on_complete:
            on_complete(md_note)
        return md_note

    def get_next_note(self, on_complete) -> "MarkdownNote":
        if not self._index:
            raise Exception("No Index")
        self._index.next()
        return self.get_note(
            category=self.current_category,
            idx=self.index.current,
            on_complete=on_complete,
        )

    def get_previous_note(self, on_complete) -> "MarkdownNote":
        if not self._index:
            raise Exception("No Index")
        self._index.previous()
        return self.get_note(
            category=self.current_category,
            idx=self.index.current,
            on_complete=on_complete,
        )

    def get_current_note(self, on_complete) -> "MarkdownNote":
        if not self._index:
            raise Exception("No Index")
        return self.get_note(
            category=self.current_category,
            idx=self.index.current,
            on_complete=on_complete,
        )

    def category_image_uri(self, category: str) -> Path | None:
        return self.category_files[category].get_image_uri()

    def category_name_unique(self, category: str) -> bool:
        """
        Checks if a category name is unique

        Parameters
        ----------
        category : str
            The category name to check
        """
        lcat = category.lower().strip()
        # Perform a case-insensitive check in our category_files dict
        if lcat in (k.lower().strip() for k in self.category_files):
            return False

        # We want to check the filesystem for any other categories but can only do this if we have a storage path.
        # We can check that we have a storage path by checking our configured attribute.
        if not self.configured:
            return True

        # Check if the directory exists, since we can access app filesystem, this is an inexpensive check
        # We can't just check if the directory exists, since we may have a category named "Foo" and "foo"
        # Create a generator of all directories in the storage path and lowercase them
        matched = next(
            (
                d
                for d in self.storage_path.iterdir()
                if d.is_dir() and d.name.lower() == lcat
            ),
            None,
        )
        return not matched
