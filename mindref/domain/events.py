import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNote

DISPLAY_STATE = Literal["choose", "display", "list", "edit", "add"]


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
    category: int


@dataclass
class NoteFetchedEvent(Event):
    event_type = "note_fetched"
    note: "MarkdownNote"


@dataclass
class NotesQueryEvent(Event):
    event_type = "notes_query"
    on_complete: Optional[Callable]


@dataclass
class RefreshNotesEvent(Event):
    event_type = "refresh_notes"
    on_complete: Callable[[], None]


@dataclass
class BackButtonEvent(Event):
    event_type = "back_button"
    display_state: DISPLAY_STATE


@dataclass
class DiscoverCategoryEvent(Event):
    """Event Emitted when a Category is detected"""

    event_type = "discover_category"
    category: str
    image_path: Optional[Path]
    notes: list[Path] = field(default_factory=list)
