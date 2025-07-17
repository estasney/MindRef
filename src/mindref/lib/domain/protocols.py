from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Literal, NoReturn, Protocol, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from kivy.uix.screenmanager import ScreenManager

    from mindref.app_notes import NoteFile
    from mindref.lib.adapters.atlas.fs.fs_atlas_repository import AtlasService
    from mindref.lib.adapters.notes.android.android_note_repository import (
        AndroidNoteRepository,
    )
    from mindref.lib.adapters.notes.fs.fs_note_repository import (
        FileSystemNoteRepository,
    )

    from mindref.lib.widgets import MindRefSettingsAndroid, MindRefSettingsNative


class AppRegistryProtocol(Protocol):
    atlas_service: AtlasService
    note_service: FileSystemNoteRepository | AndroidNoteRepository

    platform_android: bool
    error_message: str
    screen_manager: ScreenManager
    fonts: dict[str, str]
    base_font_size: int
    colors: dict[str, tuple[float, float, float] | tuple[float, float, float, float]]
    settings_cls: str | MindRefSettingsAndroid | MindRefSettingsNative
    user_data_dir: str
    note_files: list[NoteFile]

    def dispatch(self, *args, **kwargs) -> None: ...

    def select_index(self, value: int) -> None: ...

    def open_settings(self) -> None: ...

    def bind(self, **kwargs: Callable): ...

    def stop(self) -> NoReturn: ...

    def setter(self, prop: Literal["note_files"]) -> Callable: ...

    def cancel_edit_note(self) -> None: ...

    def save_edit_note(self, text: str) -> None: ...

    def cancel_draft_note(self) -> None: ...

    def save_draft_note(self, file_name: str, text: str) -> None: ...

    def load_note_files(self):
        pass

    def read_note(self, note_id: str) -> str:
        pass


T = TypeVar("T", bound=AppRegistryProtocol)
GetApp = Callable[[], T]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Path | None
    notes: list[Path]
