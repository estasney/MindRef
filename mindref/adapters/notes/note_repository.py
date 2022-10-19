from __future__ import annotations

import abc
from abc import ABC
from typing import Any, Callable, Iterable, Literal, Optional, TYPE_CHECKING, Type

from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from os import PathLike
    from domain.markdown_note import MarkdownNote, MarkdownNoteDict
    from domain.editable import EditableNote
    from domain.protocols import GetApp
    from utils.index import RollingIndex

    PLATFORM = Literal["win", "linux", "android", "macosx", "ios", "unknown"]


class NoteRepositoryFactory:
    @classmethod
    def get_repo(cls) -> Type["AbstractNoteRepository"]:
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
    _index: Optional["RollingIndex"]
    _current_category: Optional[str]
    _storage_path: Optional[Any]

    def __init__(self, get_app: "GetApp", new_first: bool):
        self.get_app = get_app
        self.new_first = new_first

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

    def get_categories(self, on_complete: Optional[Callable[[Iterable[str]], None]]):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_category(self):
        raise NotImplementedError

    @current_category.setter
    @abc.abstractmethod
    def current_category(self, value):
        raise NotImplementedError

    def get_category_meta(
        self, on_complete: Optional[Callable[[list["MarkdownNoteDict"]], None]]
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def discover_notes(self, on_complete: Optional[Callable[[], None]], *args) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_note(self, on_complete: Optional[Callable[["MarkdownNote"], None]]):
        raise NotImplementedError

    @abc.abstractmethod
    def get_previous_note(
        self, on_complete: Optional[Callable[["MarkdownNote"], None]]
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_note(self, on_complete: Optional[Callable[["MarkdownNote"], None]]):
        raise NotImplementedError

    @abc.abstractmethod
    def get_note(
        self,
        category: str,
        idx: int,
        on_complete: Optional[Callable[["MarkdownNote"], None]],
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def save_note(
        self,
        note: "EditableNote",
        on_complete: Optional[Callable[["MarkdownNote"], None]],
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
        on_complete: Optional[Callable[[Optional[list[Suggestion]]], None]],
    ):
        """String query

        Parameters
        ----------
        on_complete
        """
        raise NotImplementedError
