from collections import deque
from pathlib import Path
from typing import Callable, Optional, Protocol, TYPE_CHECKING

from domain.events import (
    DiscoverCategoryEvent,
    NoteCategoryEvent,
    NoteCategoryFailureEvent,
    NoteFetchedEvent,
    NotesQueryErrorFailureEvent,
    NotesQueryEvent,
    NotesQueryNotSetFailureEvent,
)
from utils import GenericLoggerMixin, LoggerProtocol
from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from adapters.notes.note_repository import AbstractNoteRepository
    from adapters.atlas.atlas_repository import AbstractAtlasRepository
    from adapters.editor.editor_repository import AbstractEditorRepository
    from domain.events import Event
    from domain.editable import EditableNote


class AppServiceProtocol(Protocol):
    atlas_service: "AbstractAtlasRepository"
    note_service: "AbstractNoteRepository"
    editor_service: "AbstractEditorRepository"
    note_category: str


class Registry(GenericLoggerMixin):
    """Orchestration"""

    _app: Optional["AppServiceProtocol"]
    events: deque["Event"]

    def __init__(self, logger: Optional[LoggerProtocol]):
        super().__init__()
        self._app = None
        self.logger = logger
        self.events = deque([])

    @property
    def app(self):
        if self._app is None:
            raise AttributeError(f"Registry has no App")
        return self._app

    @app.setter
    def app(self, app: "AppServiceProtocol"):
        self._app = app

    @property
    def storage_path(self):
        return self.app.note_service.storage_path

    @storage_path.setter
    def storage_path(self, path: Path):
        self.app.note_service.storage_path = path

    def push_event(self, event: "Event"):
        self.events.append(event)

    def set_note_category(self, value: str, on_complete: Optional[Callable]):
        """
        Update note_service current category.

        If Exception occurs (KeyError) push an error event
        Returns
        ------
        """
        try:
            self.app.note_service.current_category = value
        except KeyError as e:
            self.app.note_service.current_category = None
            self.push_event(
                NoteCategoryFailureEvent(on_complete=on_complete, value=value)
            )
            return
        self.push_event(NoteCategoryEvent(on_complete=on_complete, value=value))

    def query_category(
        self,
        category: str,
        query: str,
        on_complete: Callable[[Optional[list[Suggestion]]], None],
    ):
        """
        String search for a category
        """
        note_repo = self.app.note_service
        if not note_repo.configured:
            self.push_event(NotesQueryNotSetFailureEvent(on_complete=on_complete))
            return
        result = note_repo.query_notes(category=category, query=query)
        on_complete(result)

    def query_all(self, on_complete: Optional[Callable] = None):
        """
        Find available categories, their associated image and associated notes

        For each category, pushes a `DiscoverCategoryEvent`

        Finally, returns `NotesQueryEvent`

        """
        note_repo = self.app.note_service
        if not note_repo.configured:
            self.push_event(NotesQueryNotSetFailureEvent(on_complete=on_complete))
            return
        discover_pipeline = note_repo.discover_notes()
        try:
            for discovery in discover_pipeline:
                self.push_event(
                    DiscoverCategoryEvent(
                        category=discovery.category,
                        image_path=discovery.image_path,
                        notes=discovery.notes,
                    )
                )
        except FileNotFoundError as e:

            self.push_event(
                NotesQueryErrorFailureEvent(
                    on_complete=on_complete,
                    error="not_found",
                    message=f"Storage Path: '{e.filename}' not found",
                )
            )
            return
        except PermissionError as e:

            self.push_event(
                NotesQueryErrorFailureEvent(
                    on_complete=on_complete,
                    error="permission_error",
                    message=f"Permission Error: for Storage Path '{e.filename}'",
                )
            )
            return
        self.push_event(NotesQueryEvent(on_complete=on_complete))

    def new_note(self, category: Optional[str], idx: Optional[int]) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index_size() + 1
        note = self.app.editor_service.new_note(category=category, idx=idx)
        return note

    def edit_note(self, category: Optional[str], idx: Optional[int]) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index.current
        md_note = self.app.note_service.get_note(category=category, idx=idx)
        data_note = self.app.editor_service.edit_note(md_note)
        return data_note

    def save_note(self, note: "EditableNote"):
        md_note = self.app.note_service.save_note(note)
        self.push_event(NoteFetchedEvent(note=md_note))
