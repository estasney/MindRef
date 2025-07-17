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

    def read_note(self, note_id) -> str:
        pass
