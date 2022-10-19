import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generator, Literal, Optional, TYPE_CHECKING

from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNote
    from domain.protocols import NoteDiscoveryProtocol

DISPLAY_STATE = Literal["choose", "display", "list", "edit", "add", "error"]
QUERY_FAILURE_TYPE = Literal["not_set", "not_found", "permission_error"]


class Event(abc.ABC):
    @property
    @abc.abstractmethod
    def event_type(self):
        raise NotImplementedError


class EventFailure(abc.ABC):
    @property
    @abc.abstractmethod
    def message(self) -> str:
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
class NoteCategoryEvent(Event):
    event_type = "note_category"
    value: str
    on_complete: Optional[Callable]


@dataclass
class NoteCategoryFailureEvent(EventFailure, NoteCategoryEvent):
    event_type = "note_category_failure"
    message = "Could not find the category"
    error = "not_found"


@dataclass
class NotesQueryEvent(Event):
    event_type = "notes_query"
    on_complete: Optional[Callable]


@dataclass
class NotesDiscoveryEvent(Event):
    event_type = "notes_discovery"
    payload: "NoteDiscoveryProtocol"
    on_complete: Optional[Callable[[Any], None]]


@dataclass
class NotesDiscoverCategoryEvent(Event):
    """Event Emitted when a Category is detected"""

    event_type = "notes_discover_category"
    category: str
    image_path: Optional[Path]
    notes: list[Path] = field(default_factory=list)

    def __repr__(self):
        img_path = self.image_path.name if self.image_path else "None"
        return f"{self.__class__.__name__}(category={self.category}, image_path={img_path}, n_notes={len(self.notes)})"


@dataclass
class NotesQueryFailureEvent(EventFailure, NotesQueryEvent):
    event_type = "notes_query_failure"
    message = "To view notes, open Settings > Storage\n\nAnd set 'Note Storage'"
    on_complete: Optional[Callable]
    error: QUERY_FAILURE_TYPE


@dataclass
class NotesQueryNotSetFailureEvent(NotesQueryFailureEvent):
    on_complete: Optional[Callable]
    error: str = field(default="not_set")
    message: str = field(
        default="To view notes, open Settings > Storage\n\nAnd set 'Note Storage'"
    )


@dataclass
class NotesQueryErrorFailureEvent(NotesQueryFailureEvent):
    on_complete: Optional[Callable]
    error: Literal["not_found", "permission_error"]
    message: str


@dataclass
class RefreshNotesEvent(Event):
    event_type = "refresh_notes"
    on_complete: Optional[Callable[[], None]]


@dataclass
class BackButtonEvent(Event):
    event_type = "back_button"
    current_display_state: DISPLAY_STATE


@dataclass
class ListViewButtonEvent(Event):
    event_type = "list_view"


@dataclass
class TypeAheadQueryEvent(Event):
    """Event emitted by TypeAhead Query"""

    event_type = "typeahead_query"
    query: str
    on_complete: Callable[[Optional[list[Suggestion]]], None]
