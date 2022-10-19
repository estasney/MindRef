from collections import deque
from pathlib import Path
from typing import Callable, Optional, Protocol, TYPE_CHECKING

from domain.events import (
    NotesDiscoverCategoryEvent,
    NoteCategoryEvent,
    NoteCategoryFailureEvent,
    NoteFetchedEvent,
    NotesDiscoveryEvent,
    NotesQueryErrorFailureEvent,
    NotesQueryEvent,
    NotesQueryNotSetFailureEvent,
)
from utils import GenericLoggerMixin, LoggerProtocol, def_cb
from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from adapters.notes.note_repository import AbstractNoteRepository
    from adapters.atlas.atlas_repository import AbstractAtlasRepository
    from adapters.editor.editor_repository import AbstractEditorRepository
    from domain.events import Event
    from domain.editable import EditableNote
    from kivy.uix.screenmanager import ScreenManager


class AppServiceProtocol(Protocol):
    atlas_service: "AbstractAtlasRepository"
    note_service: "AbstractNoteRepository"
    editor_service: "AbstractEditorRepository"
    screen_manager: "ScreenManager"
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
        self.log(f"{self.__class__.__name__} setting app", "info")
        self._app = app

    def set_note_storage_path(self, path: Path | str):
        self.log(f"{self.__class__.__name__} setting storage_path : {path!r}", "info")
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
        result = note_repo.query_notes(category=category, query=query, on_complete=None)
        on_complete(result)

    def handle_note_discovery(self, event: NotesDiscoveryEvent):
        """
        Handles the on_complete from `self.query_all`
        """
        discover_pipeline = event.payload()
        try:
            for discovery in discover_pipeline:
                self.push_event(
                    NotesDiscoverCategoryEvent(
                        category=discovery.category,
                        image_path=discovery.image_path,
                        notes=discovery.notes,
                    )
                )
        except FileNotFoundError as e:
            self.log(f"FileNotFoundError {e}", "warning")
            self.push_event(
                NotesQueryErrorFailureEvent(
                    on_complete=event.on_complete,
                    error="not_found",
                    message=f"Storage Path: '{e.filename}' not found",
                )
            )
            return
        except PermissionError as e:
            self.push_event(
                NotesQueryErrorFailureEvent(
                    on_complete=event.on_complete,
                    error="permission_error",
                    message=f"Permission Error: for Storage Path '{e.filename}'",
                )
            )
            return
        self.push_event(NotesQueryEvent(on_complete=event.on_complete))

    def query_all(self, on_complete: Optional[Callable] = None):
        """
        Returns immediately after invoking note_repo.discover_notes

        note_repo.discover_notes will push a NotesDiscoveryEvent with results
        """
        self.app.screen_manager.dispatch("on_refresh", True)
        note_repo = self.app.note_service
        if not note_repo.configured:
            self.push_event(NotesQueryNotSetFailureEvent(on_complete=on_complete))
            return

        if on_complete:
            chained_complete = def_cb(
                on_complete,
                lambda dt: self.app.screen_manager.dispatch("on_refresh", False),
            )
        else:
            chained_complete = lambda dt: self.app.screen_manager.dispatch(
                "on_refresh", False
            )
        note_repo.discover_notes(chained_complete)

    def new_note(self, category: Optional[str], idx: Optional[int]) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index_size() + 1
        note = self.app.editor_service.new_note(category=category, idx=idx)
        return note

    def edit_note(self, category: Optional[str], idx: Optional[int]) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index.current
        md_note = self.app.note_service.get_note(
            category=category, idx=idx, on_complete=None
        )
        data_note = self.app.editor_service.edit_note(md_note)
        return data_note

    def save_note(self, note: "EditableNote"):
        md_note = self.app.note_service.save_note(note, None)
        self.push_event(NoteFetchedEvent(note=md_note))
