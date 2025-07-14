from dataclasses import dataclass
from pathlib import Path

from kivy import Logger
from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.screenmanager import ScreenManager


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
    note_files: list[NoteFile] = ListProperty()
    screen_manager: ScreenManager

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
