from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Union, Self

from kivy import Logger
from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty

if TYPE_CHECKING:
    from mindref.lib.adapters.notes.android.android_note_repository import (
        AndroidNoteRepository,
    )
    from mindref.lib.adapters.notes.fs.fs_note_repository import (
        FileSystemNoteRepository,
    )
    from mindref.lib.service import Registry
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
    registry: "Registry"
    storage_path: str
    note_service: "Union[FileSystemNoteRepository, AndroidNoteRepository]"
    note_files: list[NoteFile] = ListProperty(force_dispatch=True)

    editing_note: NoteFile | None = ObjectProperty(allownone=True)
    screen_manager: "NoteAppScreenManager"

    def query_note_files(self) -> "Self":
        if not self.storage_path:
            Logger.error(f"[{self.__class__.__name__}] Storage path is not set.")
            return self
        storage_path = Path(self.storage_path)
        if not storage_path.exists() or not storage_path.is_dir():
            Logger.error(
                f"[{self.__class__.__name__}] Storage path does not exist or is not a directory: {self.storage_path}"
            )
            return self
        note_files = sorted(
            (f for f in storage_path.rglob("**/*.md") if f.is_file()),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        self.note_files = [NoteFile.from_path(f) for f in note_files]
        self.screen_manager.dispatch("on_refresh", self, False, to_children=True)
        return self

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

    def draft_note(self):
        self.screen_manager.current = "draft_screen"

    def cancel_edit_note(self):
        self.screen_manager.current = "main_screen"
        self.editing_note = None

    def on_note_files(self, _instance, value: list[NoteFile]):
        Logger.info(
            f"[{self.__class__.__name__}] Note files updated: {len(self.note_files)} notes found."
        )

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
        self.registry.query_all_v2()
        self.cancel_edit_note()

    def cancel_draft_note(self):
        self.screen_manager.current = "main_screen"

    def save_draft_note(self, file_name: str, text: str):
        # TODO - Handle Android
        ...

        # draft_path = Path(self.user_data_dir) / "drafts" / f"{file_name}.txt"
        # draft_path.parent.mkdir(parents=True, exist_ok=True)
        # draft_path.write_text(text)
        # Logger.info(
        #     f"[{self.__class__.__name__}] Draft saved to: {draft_path}"
        # )
        # self.registry.query_all_v2()
        # self.screen_manager.current = "main_screen"
