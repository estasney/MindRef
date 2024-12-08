from __future__ import annotations

import abc
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Literal,
    Protocol,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from os import PathLike
    from pathlib import Path

    from mindref.lib.domain.editable import EditableNote
    from mindref.lib.domain.markdown_note import MarkdownNote
    from mindref.lib.domain.protocols import GetApp
    from mindref.lib.ext import RollingIndex

    from ...domain.settings import SortOptions
    from .android.android_note_repository import AndroidNoteRepository
    from .fs.fs_note_repository import FileSystemNoteRepository

    PLATFORM = Literal["win", "linux", "android", "macosx", "ios", "unknown"]


# noinspection PyUnusedLocal
class NoteRepositoryInitProtocol(Protocol):
    def __init__(
        self,
        get_app: GetApp,
        note_sorting: SortOptions,
        note_sorting_ascending: bool,
        category_sorting: SortOptions,
        category_sorting_ascending: bool,
        **kwargs,
    ): ...


class NoteRepositoryFactory:
    @classmethod
    def _get_repo_android(cls) -> type[AndroidNoteRepository]:
        from .android.android_note_repository import AndroidNoteRepository

        return AndroidNoteRepository

    @classmethod
    def _get_repo_default(cls) -> type[FileSystemNoteRepository]:
        from .fs.fs_note_repository import FileSystemNoteRepository

        return FileSystemNoteRepository

    @classmethod
    def get_repo(cls) -> type[FileSystemNoteRepository] | type[AndroidNoteRepository]:
        """
        Dynamic Class returned based on platform.
        """

        from kivy import platform

        match platform:
            case "android":
                return cls._get_repo_android()
            case _:
                return cls._get_repo_default()


class AbstractNoteRepository(ABC):
    @property
    @abc.abstractmethod
    def configured(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def storage_path(self):
        raise NotImplementedError

    @storage_path.setter
    def storage_path(self, path: PathLike | None):
        raise NotImplementedError

    def get_categories(self, on_complete: Callable) -> list[str]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_category(self):
        raise NotImplementedError

    @current_category.setter
    @abc.abstractmethod
    def current_category(self, value: str):
        raise NotImplementedError

    @abc.abstractmethod
    def create_category(self, name: str, image_path: Path | str, on_complete: Callable):
        raise NotImplementedError

    def get_category_meta(
        self, category: str, on_complete: Callable, refresh: bool = False
    ):
        """For self.current_category, get MarkdownNoteDict for all files in category

        Parameters
        ----------
        category
        on_complete
        refresh : bool
            If False, (default) don't force-reload of MarkdownNotes
            If True, force-reload
        """
        raise NotImplementedError

    @abc.abstractmethod
    def discover_categories(self, on_complete: Callable) -> None:
        """Discover all categories and emit a DiscoverCategoryEvent"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_note(self, on_complete: Callable | None) -> MarkdownNote:
        raise NotImplementedError

    @abc.abstractmethod
    def get_previous_note(self, on_complete: Callable | None) -> MarkdownNote:
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_note(self, on_complete: Callable | None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_note(self, category: str, idx: int, on_complete: Callable | None):
        raise NotImplementedError

    @abc.abstractmethod
    def save_note(
        self,
        note: EditableNote,
        on_complete: Callable,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def set_index(self, n: int | None):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def index(self) -> RollingIndex:
        raise NotImplementedError

    @abc.abstractmethod
    def index_size(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def category_image_uri(self, category: str):
        """Return URI for a Category Image"""
        raise NotImplementedError

    @abc.abstractmethod
    def query_notes(
        self,
        category: str,
        query: str,
        on_complete: Callable | None,
    ):
        """Search Notes

        Parameters
        ----------
        category: str
        query: str
            String query to search
        on_complete
        """
        raise NotImplementedError

    @abc.abstractmethod
    def category_name_unique(self, category: str) -> bool:
        """Return True if category name is unique"""
        raise NotImplementedError
