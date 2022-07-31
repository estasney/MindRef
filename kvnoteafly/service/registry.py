from collections import deque
from pathlib import Path
from typing import Optional, Type, Callable, TYPE_CHECKING, Protocol
from domain.events import DiscoverCategoryEvent, NoteFetchedEvent, NotesQueryEvent
from utils import GenericLoggerMixin, LoggerProtocol

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

    def query_all(self, on_complete: Optional[Callable] = None):
        """
        Find available categories, their associated image and associated notes

        For each category, pushes a `DiscoverCategoryEvent`

        Finally, returns `NotesQueryEvent`

        """
        note_repo = self.app.note_service
        discover_pipeline = note_repo.discover_notes()
        for discovery in discover_pipeline:
            self.push_event(
                DiscoverCategoryEvent(
                    category=discovery.category,
                    image_path=discovery.image_path,
                    notes=discovery.notes,
                )
            )
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
