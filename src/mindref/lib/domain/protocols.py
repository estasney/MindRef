from __future__ import annotations

from collections.abc import Callable
from concurrent.futures.thread import ThreadPoolExecutor
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from kivy.uix.screenmanager import ScreenManager

    from mindref.app_notes import NoteFile
    from mindref.lib.adapters.atlas.fs.fs_atlas_repository import AtlasService
    from mindref.lib.adapters.base import FileSystemBase
    from mindref.lib.widgets.settings.settings_mindref import MindrefSettings


class AppRegistryProtocol(Protocol):
    atlas_service: AtlasService
    fs: FileSystemBase
    platform_android: bool
    error_message: str
    screen_manager: ScreenManager
    fonts: dict[str, str]
    base_font_size: int
    colors: dict[str, tuple[float, float, float] | tuple[float, float, float, float]]
    settings_cls: str | MindrefSettings
    user_data_dir: str
    pool: ThreadPoolExecutor
    note_files: list[NoteFile]

    def open_settings(self, *largs: object) -> bool: ...

    def bind(self, **kwargs: Callable[..., object]) -> None: ...

    def stop(self, *largs: object) -> None: ...

    def cancel_edit_note(self) -> None: ...

    def save_edit_note(self, text: str) -> None: ...

    def save_draft_note(self, file_name: str, text: str) -> None: ...

    def refresh_note_files(self) -> None: ...

    def read_note(self, note_id: str) -> str: ...


T = TypeVar("T", bound=AppRegistryProtocol)
GetApp = Callable[[], T]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Path | None
    notes: list[Path]
