import abc
from abc import ABC
from typing import Callable, Literal, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from services.domain import MarkdownNote
    from services.editor import TextNote, EditableNote


class BackendProtocol(ABC):
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
    def _discover_notes(self):
        raise NotImplementedError

    @abc.abstractmethod
    def next_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def previous_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def current_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set_index(self, n: Optional[int]):
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_categories(self):
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_current_category(self):
        raise NotImplementedError

    @abc.abstractmethod
    def save_note_listener(
        self,
        event: Literal["save_note"],
        note: "Union[TextNote, EditableNote]",
        callback: "Callable[[MarkdownNote], None]",
    ):
        raise NotImplementedError


class NoteIndex:
    """
    Handles indexing notes so that we can always call `next` or `previous`

    As with `range`, `end` is not inclusive
    """

    def __init__(self, size: int, current=0):
        self.size = size
        self.start = 0
        self.end = max([0, (size - 1)])
        self.current = current

    def set_current(self, n: int):
        if n >= self.size:
            raise IndexError(f"{n} is greater the {self.size}")
        self.current = n

    def next(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == self.end:
            self.current = 0
            return self.current
        else:
            self.current += 1
            return self.current

    def previous(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == 0:
            self.current = self.end
            return self.current
        else:
            self.current -= 1
            return self.current
