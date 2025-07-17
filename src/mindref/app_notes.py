from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty

from mindref.lib.adapters_v2.direct_file_system import DirectFileSystemAdapter
from mindref.lib.adapters_v2.file_system import FileSystemBase
from mindref.lib.mutation import Mutation

if TYPE_CHECKING:
    from mindref.screens.manager import NoteAppScreenManager


@dataclass
class NoteFile:
    file_path: Path
    label: str
    id: str

    def __post_init__(self):
        self.file_path = Path(self.file_path)
        self.label = self.file_path.stem
        self.id = str(self.file_path)

    @classmethod
    def from_path(cls, path: str | Path) -> "NoteFile":
        path = Path(path)
        return cls(file_path=path, label=path.stem, id=str(path))

    def read_text(self, encoding: str = "utf-8") -> str:
        """Read the content of the note file."""
        return self.file_path.read_text(encoding=encoding)


class AppNotesMixin(App):
    storage_path: Path
    note_files: list[NoteFile] = ListProperty(force_dispatch=True)
    editing_note: NoteFile | None = ObjectProperty(allownone=True)
    screen_manager: "NoteAppScreenManager"
    notes_files_mutation: Mutation
    fs: FileSystemBase

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes_files_mutation = Mutation(self._query_note_files)
        self.notes_files_mutation.bind(
            on_mutate=self.handle_note_file_mutation,
            on_resolved=self.handle_note_file_resolved,
            on_success=self.handle_note_file_success,
        )
        self.fs = DirectFileSystemAdapter()

    def handle_note_file_mutation(self, _dt):
        self.screen_manager.dispatch("on_refresh", self, True, to_children=True)

    def handle_note_file_resolved(self, _dt):
        self.screen_manager.dispatch("on_refresh", self, False, to_children=True)

    def handle_note_file_success(self, _dt, result: list[NoteFile]):
        Logger.info(
            f"[{self.__class__.__name__}] Note files successfully queried: {len(result)} files found."
        )
        self.note_files = result
        self.screen_manager.dispatch("on_refresh", self, False, to_children=True)

    def load_note_files(self, *_args):
        Logger.info(
            f"[{self.__class__.__name__}] Loading note files from storage path."
        )
        Clock.schedule_once(
            lambda _: self.notes_files_mutation(),
        )

    def _query_note_files(self) -> list[NoteFile]:
        storage_path = self.storage_path
        if not storage_path:
            Logger.error(f"[{self.__class__.__name__}] Storage path is not set.")
            return self.note_files

        return self.fs.query_note_files(self.storage_path)

    def read_note(self, note_id: str) -> str:
        """Read the contents of the note"""
        # TODO Use FileSystem
        matched_note = next(
            (note for note in self.note_files if note.id == note_id), None
        )
        if not matched_note:
            Logger.error(
                f"[{self.__class__.__name__}] Note with ID {note_id} not found."
            )
            return ""
        return matched_note.read_text(encoding="utf-8")

    def edit_note(self, note_id: str):
        matched_note = next(
            (note for note in self.note_files if note.id == note_id), None
        )
        if not matched_note:
            Logger.error(
                f"[{self.__class__.__name__}] Note with ID {note_id} not found."
            )
            return
        Logger.info(
            f"[{self.__class__.__name__}] Editing note: {matched_note.file_path}"
        )
        self.editing_note = matched_note
        self.screen_manager.current = "edit_screen"

    def cancel_edit_note(self, *_args):
        self.screen_manager.current = "main_screen"
        self.editing_note = None

    def save_edit_note(self, text: str):
        if not self.editing_note:
            Logger.error(
                f"[{self.__class__.__name__}] No note is currently being edited."
            )
            return
        Logger.info(
            f"[{self.__class__.__name__}] Saving changes to note: {self.editing_note.file_path}"
        )
        self.editing_note.file_path.write_text(text)

        self.load_note_files()
        Clock.schedule_once(self.cancel_edit_note)

    def draft_note(self):
        self.screen_manager.current = "draft_screen"

    def cancel_draft_note(self):
        self.screen_manager.current = "main_screen"

    def save_draft_note(self, file_name: str, text: str):
        # TODO - Handle Android
        draft_path = (Path(self.storage_path) / file_name).with_suffix(".md")
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(text, encoding="utf-8")

        note_files = [NoteFile.from_path(draft_path), *self.note_files]
        self.note_files = note_files
        self.screen_manager.current = "main_screen"
