import abc
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNote


class Event(abc.ABC):
    @property
    @abc.abstractmethod
    def event_type(self):
        raise NotImplementedError


@dataclass
class CancelEditEvent(Event):
    event_type = "cancel_edit"


@dataclass
class AddNoteEvent(Event):
    event_type = "add_note"


@dataclass
class EditNoteEvent(Event):
    event_type = "edit_note"
    category: str
    idx: int


@dataclass
class SaveNoteEvent(Event):
    event_type = "save_note"
    text: str
    title: Optional[str]


@dataclass
class NoteFetched(Event):
    event_type = "note_fetched"
    note: "MarkdownNote"
