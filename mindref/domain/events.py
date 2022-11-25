import abc
from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNote
    from domain.protocols import NoteDiscoveryProtocol
    from mindref.mindref import DISPLAY_STATE
    from widgets.typeahead.typeahead_dropdown import Suggestion

    QUERY_FAILURE_TYPE = Literal["not_set", "not_found", "permission_error"]
    PAGINATION_DIRECTION = Literal[-1, 0, 1]


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
class PaginationEvent(Event):
    """Emitted when we want to display a note_screen"""

    event_type = "pagination"
    direction: "PAGINATION_DIRECTION"

    def __repr__(self):
        attrs = ("event_type", "direction")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class CancelEditEvent(Event):
    event_type = "cancel_edit"

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class AddNoteEvent(Event):
    event_type = "add_note"

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class EditNoteEvent(Event):
    event_type = "edit_note"
    category: str
    idx: int

    def __repr__(self):
        attrs = ("event_type", "category", "idx")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class SaveNoteEvent(Event):
    event_type = "save_note"
    text: str
    title: Optional[str]
    category: str

    def __repr__(self):
        attrs = ("event_type", "title", "category")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NoteFetchedEvent(Event):
    event_type = "note_fetched"
    note: "MarkdownNote"

    def __repr__(self):
        attrs = ("event_type", "note")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NoteCategoryEvent(Event):
    event_type = "note_category"
    value: str
    on_complete: Optional[Callable]

    def __repr__(self):
        attrs = ("event_type", "value", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NoteCategoryFailureEvent(EventFailure, NoteCategoryEvent):
    event_type = "note_category_failure"
    message = "Could not find the category"
    error = "not_found"

    def __repr__(self):
        attrs = ("event_type", "error")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NotesQueryEvent(Event):
    event_type = "notes_query"
    on_complete: Optional[Callable]

    def __repr__(self):
        attrs = ("event_type", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NotesDiscoveryEvent(Event):
    event_type = "notes_discovery"
    payload: "NoteDiscoveryProtocol"
    on_complete: Optional[Callable[[Any], None]]

    def __repr__(self):
        attrs = ("event_type", "payload", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class DiscoverCategoryEvent(Event):
    """Event Emitted when a Category is detected"""

    event_type = "discover_category"
    category: str

    def __repr__(self):
        attrs = ("event_type", "category")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NotesQueryFailureEvent(EventFailure, NotesQueryEvent):
    event_type = "notes_query_failure"
    message = "To view notes, open Settings > Storage\n\nAnd set 'Note Storage'"
    on_complete: Optional[Callable]
    error: "QUERY_FAILURE_TYPE"

    def __repr__(self):
        attrs = ("event_type", "on_complete", "error")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NotesQueryNotSetFailureEvent(NotesQueryFailureEvent):
    on_complete: Optional[Callable]
    error: str = field(default="not_set")
    message: str = field(
        default="To view notes, open Settings > Storage\n\nAnd set 'Note Storage'"
    )

    def __repr__(self):
        attrs = ("event_type", "error", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class NotesQueryErrorFailureEvent(NotesQueryFailureEvent):
    on_complete: Optional[Callable]
    error: Literal["not_found", "permission_error"]
    message: str

    def __repr__(self):
        attrs = ("error", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class RefreshNotesEvent(Event):
    event_type = "refresh_notes"
    on_complete: Optional[Callable[[], None]]

    def __repr__(self):
        attrs = ("event_type", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class BackButtonEvent(Event):
    event_type = "back_button"
    display_state: "DISPLAY_STATE"

    def __repr__(self):
        attrs = ("event_type", "display_state")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class ListViewButtonEvent(Event):
    event_type = "list_view"

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"


@dataclass
class TypeAheadQueryEvent(Event):
    """Event emitted by TypeAhead Query"""

    event_type = "typeahead_query"
    query: str
    on_complete: Callable[[Optional[list["Suggestion"]]], None]

    def __repr__(self):
        attrs = ("event_type", "query", "on_complete")
        return f"{type(self).__name__}({','.join((f'{p}={getattr(self, p)}' for p in attrs))})"
