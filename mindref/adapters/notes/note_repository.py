from __future__ import annotations

import abc
from abc import ABC
from typing import Callable, Literal, Optional, Protocol, TYPE_CHECKING, Type, overload

if TYPE_CHECKING:
    from os import PathLike
    from domain.markdown_note import MarkdownNote
    from domain.editable import EditableNote
    from domain.protocols import GetApp
    from utils.index import RollingIndex
    from .android.android_note_repository import AndroidNoteRepository
    from .fs.fs_note_repository import FileSystemNoteRepository

    PLATFORM = Literal["win", "linux", "android", "macosx", "ios", "unknown"]


# noinspection PyUnusedLocal
class NoteRepositoryInitProtocol(Protocol):
    def __init__(self, get_app: "GetApp", new_first: bool):
        ...


class NoteRepositoryFactory:
    @classmethod
    @overload
    def get_repo(cls) -> "Type[AndroidNoteRepository]":
        ...

    @classmethod
    @overload
    def get_repo(cls) -> "Type[FileSystemNoteRepository]":
        ...

    @classmethod
    def get_repo(cls):
        """
        Dynamic Class returned based on platform.
        """

        from kivy import platform  # noqa

        platform: PLATFORM
        match platform:
            case "android":
                from .android.android_note_repository import AndroidNoteRepository

                return AndroidNoteRepository
            case _:
                from .fs.fs_note_repository import FileSystemNoteRepository

                return FileSystemNoteRepository


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
    def storage_path(self, path: "PathLike"):
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

    def get_category_meta(self, category: str, on_complete: Callable, refresh=False):
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
    def get_next_note(self, on_complete: Optional[Callable]) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def get_previous_note(self, on_complete: Optional[Callable]) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_note(self, on_complete: Optional[Callable]):
        raise NotImplementedError

    @abc.abstractmethod
    def get_note(self, category: str, idx: int, on_complete: Optional[Callable]):
        raise NotImplementedError

    @abc.abstractmethod
    def save_note(
        self,
        note: "EditableNote",
        on_complete: Callable,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def set_index(self, n: Optional[int]):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def index(self) -> "RollingIndex":
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
        on_complete: Optional[Callable],
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
