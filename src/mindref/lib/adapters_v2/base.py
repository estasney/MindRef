from abc import ABC, abstractmethod
from pathlib import Path

from mindref.app_notes import NoteFile


class FileSystemBase(ABC):
    external_storage_path: str | None

    @abstractmethod
    def refresh_note_files(
        self, storage_path: str | Path, external_storage_path: str
    ) -> list["NoteFile"]: ...
    @abstractmethod
    def read_note(self, note_id: str, note_files: list["NoteFile"]) -> str: ...
    @abstractmethod
    def save_draft_note(
        self,
        storage_path: str | Path,
        external_storage_path: str,
        file_name: str,
        text: str,
    ) -> "NoteFile": ...
    @abstractmethod
    def save_edit_note(
        self,
        storage_path: str | Path,
        external_storage_path: str,
        file_name: str,
        text: str,
    ) -> "NoteFile": ...
