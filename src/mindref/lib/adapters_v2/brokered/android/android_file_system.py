from pathlib import Path
from typing import TYPE_CHECKING

from ...direct_file_system import DirectFileSystemAdapter
from .external_storage import ExternalStorageMixin

if TYPE_CHECKING:
    from mindref.app_notes import NoteFile


class AndroidFileSystemAdapter(DirectFileSystemAdapter, ExternalStorageMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.external_storage_path = ""

    def query_note_files(self, storage_path: str | Path) -> list["NoteFile"]:
        return super().query_note_files(storage_path)

    def read_note(self, note_id: str, note_files: list["NoteFile"]) -> str:
        return super().read_note(note_id, note_files)

    def save_draft_note(
        self, storage_path: str | Path, file_name: str, text: str
    ) -> "NoteFile":
        local_result = super().save_draft_note(storage_path, file_name, text)
        return local_result
        # TODO - Then persist this to External Storage

    def save_edit_note(
        self, storage_path: str | Path, file_name: str, text: str
    ) -> "NoteFile":
        local_result = super().save_edit_note(storage_path, file_name, text)
        # TODO - Then persist this to External Storage
        return local_result
