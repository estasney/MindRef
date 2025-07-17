from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mindref.app_notes import NoteFile


class FileSystemBase(ABC):
    @abstractmethod
    def query_note_files(self, storage_path: str | Path) -> list["NoteFile"]: ...
    @abstractmethod
    def read_note(self, note_id: str, note_files: list["NoteFile"]) -> str: ...
    @abstractmethod
    def save_draft_note(
        self, storage_path: str | Path, file_name: str, text: str
    ) -> "NoteFile": ...
    @abstractmethod
    def save_edit_note(
        self, storage_path: str | Path, file_name: str, text: str
    ) -> "NoteFile": ...
