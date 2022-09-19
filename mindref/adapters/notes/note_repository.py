from __future__ import annotations

import abc
from abc import ABC
from typing import Any, Generator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike
    from domain.markdown_note import MarkdownNote
    from domain.editable import EditableNote
    from domain.protocols import GetApp, NoteDiscoveryProtocol
    from utils.index import RollingIndex


class AbstractNoteRepository(ABC):
    _index: Optional["RollingIndex"]
    _current_category: Optional[str]
    _storage_path: Optional[Any]

    def __init__(self, get_app: "GetApp"):
        self.get_app = get_app

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

    @property
    @abc.abstractmethod
    def categories(self) -> list[str]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_category(self):
        raise NotImplementedError

    @current_category.setter
    @abc.abstractmethod
    def current_category(self, value):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def category_meta(self):
        raise NotImplementedError

    @abc.abstractmethod
    def discover_notes(self) -> Generator["NoteDiscoveryProtocol", None, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def next_note(self) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def previous_note(self) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def current_note(self) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def get_note(self, category: str, idx: int) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def save_note(self, note: "EditableNote") -> "MarkdownNote":
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
