import abc
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Flag, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from lib import DisplayState

if TYPE_CHECKING:
    from lib.domain.markdown_note import MarkdownNote
    from lib.domain.protocols import NoteDiscoveryProtocol
    from lib.widgets.typeahead.typeahead_dropdown import Suggestion

    QUERY_FAILURE_TYPE = Literal["not_set", "not_found", "permission_error"]
    PAGINATION_DIRECTION = Literal[-1, 0, 1]


class Event:

    event_type: ClassVar[str]


class EventFailure:

    message: ClassVar[str]


@dataclass(slots=True)
class PaginationEvent(Event):
    """Emitted when we want to display a note_screen"""

    event_type = "pagination"
    direction: "PAGINATION_DIRECTION"

    def __repr__(self):
        attrs = ("event_type", "direction")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class CancelEditEvent(Event):
    event_type = "cancel_edit"

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class AddNoteEvent(Event):
    event_type = "add_note"

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class EditNoteEvent(Event):
    event_type = "edit_note"
    category: str
    idx: int

    def __repr__(self):
        attrs = ("event_type", "category", "idx")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class SaveNoteEvent(Event):
    event_type = "save_note"
    text: str
    title: str | None
    category: str

    def __repr__(self):
        attrs = ("event_type", "title", "category")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NoteFetchedEvent(Event):
    event_type = "note_fetched"
    note: "MarkdownNote"

    def __repr__(self):
        attrs = ("event_type", "note")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NoteCategoryEvent(Event):
    event_type = "note_category"
    value: str | None
    on_complete: Callable | None

    def __repr__(self):
        attrs = ("event_type", "value", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NoteCategoryFailureEvent(EventFailure, NoteCategoryEvent):
    event_type = "note_category_failure"
    message = "Could not find the category"
    error = "not_found"

    def __repr__(self):
        attrs = ("event_type", "error")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NotesQueryEvent(Event):
    event_type = "notes_query"
    on_complete: Callable | None

    def __repr__(self):
        attrs = ("event_type", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NotesDiscoveryEvent(Event):
    event_type = "notes_discovery"
    payload: "NoteDiscoveryProtocol"
    on_complete: Callable[[Any], None] | None

    def __repr__(self):
        attrs = ("event_type", "payload", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class DiscoverCategoryEvent(Event):
    """Event Emitted when a Category is detected"""

    event_type = "discover_category"
    category: str

    def __repr__(self):
        attrs = ("event_type", "category")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class CreateCategoryEvent(Event):
    class Action(Flag):
        OPEN_FORM = auto()
        CLOSE_FORM = auto()
        ACCEPT = auto()
        REJECT = auto()
        CLOSE_REJECT = CLOSE_FORM | REJECT
        CLOSE_ACCEPT = CLOSE_FORM | ACCEPT

    action: Action
    event_type = "create_category"
    category: str | None = None
    img_path: str | Path | None = None


@dataclass(slots=True)
class NotesQueryFailureEvent(EventFailure, NotesQueryEvent):
    event_type = "notes_query_failure"
    message = "To view notes, open Settings > Storage\n\nAnd set 'Note Storage'"
    on_complete: Callable | None
    error: "QUERY_FAILURE_TYPE"

    def __repr__(self):
        attrs = ("event_type", "on_complete", "error")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NotesQueryNotSetFailureEvent(NotesQueryFailureEvent):
    on_complete: Callable | None
    error: "QUERY_FAILURE_TYPE" = field(default="not_set")
    message = "To view notes, open Settings > Storage\n\nAnd set 'Note Storage'"

    def __repr__(self):
        attrs = ("event_type", "error", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class NotesQueryErrorFailureEvent(NotesQueryFailureEvent):
    on_complete: Callable | None
    error: Literal["not_found", "permission_error"]
    message: str

    def __repr__(self):
        attrs = ("error", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class RefreshNotesEvent(Event):
    event_type = "refresh_notes"
    on_complete: Callable[[], None] | None

    def __repr__(self):
        attrs = ("event_type", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class BackButtonEvent(Event):
    event_type = "back_button"
    display_state: DisplayState

    def __repr__(self):
        attrs = ("event_type", "display_state")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class ListViewButtonEvent(Event):
    event_type = "list_view"

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class TypeAheadQueryEvent(Event):
    """Event emitted by TypeAhead Query"""

    event_type = "typeahead_query"
    query: str
    on_complete: Callable[[list["Suggestion"] | None], None]

    def __repr__(self):
        attrs = ("event_type", "query", "on_complete")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"


@dataclass(slots=True)
class FilePickerEvent(Event):
    """
    Any event dispatched when the event is to open a platform specific file/folder picker
    """

    class Action(Flag):
        OPEN = auto()
        CLOSE = auto()
        FILE = auto()
        FOLDER = auto()
        OPEN_FILE = OPEN | FILE
        OPEN_FOLDER = OPEN | FOLDER

    event_type = "file_picker"
    on_complete: Callable[[str], None] | None
    action: Action
    start_folder: str | None = None
    ext_filter: list[str] | Callable[[tuple[str, str]], bool] | None = None

    def __repr__(self):
        attrs = ("event_type",)
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"
