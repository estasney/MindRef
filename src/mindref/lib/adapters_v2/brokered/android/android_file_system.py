from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from mindref.lib.android.interface import V2MindRefCallCodes

from ...direct_file_system import DirectFileSystemAdapter

if TYPE_CHECKING:
    from mindref.app_notes import NoteFile

TPromptExternalStorageCallback = Callable[[str], None]


class AndroidFileSystemAdapter(DirectFileSystemAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from mindref.lib.android.interface import AndroidManager  # noqa: PLC0415

        self.android_manager = AndroidManager()
        self.android_manager.set_py_mediator(self.py_mediator)
        self.py_callbacks: dict[V2MindRefCallCodes, Callable] = {}

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

    def py_mediator(self) -> Callable[[V2MindRefCallCodes, tuple[Any, ...]], None]:
        return self.py_mediator_impl

    def py_mediator_impl(self, key: V2MindRefCallCodes, *args) -> None: ...

    def prompt_for_external_storage(
        self, callback: TPromptExternalStorageCallback
    ) -> None:
        """
        Prompts the user to select a file or folder from external storage.

        Parameters
        ----------
        callback : TKeyedCallback
            A callback function that will be called with the result of the user's selection.
        """
        self.py_callbacks[V2MindRefCallCodes.PROMPT_EXTERNAL_STORAGE] = callback
        self.android_manager.prompt_for_external_storage()
