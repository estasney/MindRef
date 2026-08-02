from collections.abc import Callable
from concurrent.futures import Future
from pathlib import Path
from typing import TYPE_CHECKING

from kivy.clock import Clock, mainthread
from kivy.logger import Logger

from mindref.lib import get_app, schedulable
from mindref.lib.adapters.base import FileSystemBase
from mindref.lib.adapters.brokered.android.types import (
    MindRefUtilsCallbackPyMediator,
    V2MindRefCallCodes,
)

if TYPE_CHECKING:
    from mindref.app_notes import NoteFile

TPromptExternalStorageCallback = Callable[[str], None]
TImportExternalStorageCallback = Callable[[], None]
TCopyToExternalStorageCallback = Callable[[str], None]


class AndroidFileSystemAdapter(FileSystemBase):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.app = get_app()
        from mindref.lib.adapters.brokered.android.external_storage import (
            AndroidManager,
        )

        self.android_manager = AndroidManager()
        self.android_manager.set_py_mediator(self.py_mediator)
        self.py_callbacks: dict[int, Callable[..., None]] = {}

    def _import_note_files(
        self, storage_path: str | Path, external_storage_path: str
    ) -> Future[bool]:
        # Before we hand off to Android Manager, we need to setup a callback to notify us that import is complete
        # That callback ? Refresh our notes from app storage. But we need to wait on the JNI method to complete first.

        fut: Future[bool] = Future()

        # Sentinel to notify us that import is complete
        self.py_callbacks[V2MindRefCallCodes.IMPORT_EXTERNAL_STORAGE] = lambda: (
            fut.set_result(True)
        )

        # We want to return Future immediately but still need this ro run
        def start_import(_dt: float) -> None:
            self.android_manager.import_external_storage(
                external_storage_path, str(storage_path)
            )

        Clock.schedule_once(start_import)

        return fut

    def _refresh_note_files(self, storage_path: str | Path) -> list["NoteFile"]:
        """
        Refreshes the note files from the given storage path.
        """
        Logger.info(
            f"{self.__class__.__name__} : Refreshing note files from {storage_path}"
        )
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

    def refresh_note_files(
        self, storage_path: str | Path, external_storage_path: str
    ) -> list["NoteFile"]:
        """
        This is the complicated bit about Android. We treat `external_storage_path` as SOT
        for notes. So before we can 'refresh', we must ensure our `storage_path` is synced with `external_storage_path`

        Note: This is a blocking call, call this from a thread

        """

        if not external_storage_path or external_storage_path == "":
            Logger.info(
                f"{self.__class__.__name__} : No external storage path provided, skipping import."
            )
            return self._refresh_note_files(storage_path)

        # Blocking Call ! Run in
        import_fut = self._import_note_files(
            storage_path=storage_path, external_storage_path=external_storage_path
        )
        Logger.info(f"{self.__class__.__name__} : Waiting on Import to complete")
        import_fut.result(15)
        Logger.info(f"{self.__class__.__name__} : Import completed - now refreshing")

        # Resume normality
        return self._refresh_note_files(storage_path)

    def read_note(self, note_id: str, note_files: list["NoteFile"]) -> str:
        matched_note = next((note for note in note_files if note.id == note_id), None)
        if not matched_note:
            Logger.error(
                f"[{self.__class__.__name__}] Note with ID {note_id} not found."
            )
            return ""
        return matched_note.read_text(encoding="utf-8")

    def save_draft_note(
        self,
        storage_path: str | Path,
        external_storage_path: str,
        file_name: str,
        text: str,
    ) -> "NoteFile":
        # Saving it locally to App Storage - Fast
        storage_path = Path(storage_path)
        draft_path = (storage_path / file_name).with_suffix(".md")
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(text, encoding="utf-8")
        from mindref.app_notes import NoteFile

        note_file = NoteFile.from_path(draft_path)

        # Dispatch to MindRefUtils, using a thread to copy to external storage

        def handle_copy_complete(*args: object, **kwargs: object) -> None:
            Logger.info(
                f"{self.__class__.__name__} : Draft note saved to external storage: {note_file.file_path}"
            )

        def handle_copy() -> None:
            self.copy_to_external_storage(
                external_storage_path,
                storage_path,
                str(draft_path),
                callback=handle_copy_complete,
            )

        self.app.pool.submit(handle_copy)

        Logger.info(
            f"{self.__class__.__name__} : Draft note saved locally: {note_file.file_path}"
        )

        return note_file

    def save_edit_note(
        self,
        storage_path: str | Path,
        external_storage_path: str,
        file_name: str,
        text: str,
    ) -> "NoteFile":
        storage_path = Path(storage_path)
        edit_path = (storage_path / file_name).with_suffix(".md")
        edit_path.parent.mkdir(parents=True, exist_ok=True)
        edit_path.write_text(text, encoding="utf-8")
        from mindref.app_notes import NoteFile

        note_file = NoteFile.from_path(edit_path)

        # Dispatch to MindRefUtils, using a thread to copy to external storage

        def handle_copy_complete(*args: object, **kwargs: object) -> None:
            Logger.info(
                f"{self.__class__.__name__} : Edit note saved to external storage: {note_file.file_path}"
            )

        def handle_copy() -> None:
            self.copy_to_external_storage(
                external_storage_path,
                storage_path,
                str(edit_path),
                callback=handle_copy_complete,
            )

        self.app.pool.submit(handle_copy)

        Logger.info(
            f"{self.__class__.__name__} : Edit note saved locally: {note_file.file_path}"
        )

        return note_file

    def py_mediator(self) -> MindRefUtilsCallbackPyMediator:
        return self.py_mediator_impl

    @mainthread
    def py_mediator_impl(self, key: int, *args: object) -> None:
        Logger.info(
            f"AndroidFileSystemAdapter: py_mediator called with key={key}, args={args}"
        )
        callback = self.py_callbacks.pop(key, None)
        if callback is None:
            raise ValueError(f"Callback for key {key} not found in py_callbacks.")
        Logger.info(
            f"AndroidFileSystemAdapter: Calling callback={callback} for key={key} with args={args}"
        )
        callback(*args)

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

        Clock.schedule_once(
            schedulable(
                self.android_manager.prompt_for_external_storage,
            )
        )

    def copy_to_external_storage(
        self,
        external_storage_path: str,
        storage_path: str | Path,
        filePath: str | Path,
        callback: TCopyToExternalStorageCallback,
    ) -> None:
        self.py_callbacks[V2MindRefCallCodes.COPY_TO_EXTERNAL_STORAGE] = callback
        self.android_manager.copy_to_external_storage(
            external_storage_path, str(storage_path), str(filePath)
        )
