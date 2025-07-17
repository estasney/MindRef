from pathlib import Path
from typing import TYPE_CHECKING

from kivy import Logger

from . import FileSystemBase

if TYPE_CHECKING:
    from ...app_notes import NoteFile


class DirectFileSystemAdapter(FileSystemBase):
    def query_note_files(self, storage_path: str | Path) -> list["NoteFile"]:
        storage_path = Path(storage_path)
        if not storage_path.exists() or not storage_path.is_dir():
            Logger.error(
                f"[{self.__class__.__name__}] Storage path does not exist or is not a directory: {storage_path}"
            )
            return []
        note_files = sorted(
            (f for f in storage_path.rglob("**/*.md") if f.is_file()),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        from mindref.app_notes import NoteFile

        return [NoteFile.from_path(f) for f in note_files]

    def read_note(self, note_id: str, note_files: list["NoteFile"]) -> str:
        matched_note = next((note for note in note_files if note.id == note_id), None)
        if not matched_note:
            Logger.error(
                f"[{self.__class__.__name__}] Note with ID {note_id} not found."
            )
            return ""
        return matched_note.read_text(encoding="utf-8")

    def save_draft_note(
        self, storage_path: str | Path, file_name: str, text: str
    ) -> "NoteFile":
        storage_path = Path(storage_path)
        draft_path = (storage_path / file_name).with_suffix(".md")
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(text, encoding="utf-8")
        from mindref.app_notes import NoteFile

        return NoteFile.from_path(draft_path)

    def save_edit_note(
        self, storage_path: str | Path, file_name: str, text: str
    ) -> "NoteFile":
        storage_path = Path(storage_path)
        edit_path = (storage_path / file_name).with_suffix(".md")
        edit_path.parent.mkdir(parents=True, exist_ok=True)
        edit_path.write_text(text, encoding="utf-8")
        from mindref.app_notes import NoteFile

        return NoteFile.from_path(edit_path)
