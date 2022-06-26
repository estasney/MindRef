from collections import deque
from pathlib import Path
from typing import Optional, Type, Callable, TYPE_CHECKING, Protocol
from domain.events import NoteFetched
from utils import GenericLoggerMixin, LoggerProtocol

if TYPE_CHECKING:
    from adapters.notes.note_repository import AbstractNoteRepository, NoteDiscovery
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

    def query_all(self) -> list["NoteDiscovery"]:
        """
        Find available categories, their associated image and associated notes
        Returns
        -------

        """
        note_repo = self.app.note_service
        return note_repo.discover_notes()

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
        self.push_event(NoteFetched(note=md_note))
