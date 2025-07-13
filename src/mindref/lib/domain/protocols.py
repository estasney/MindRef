from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, NoReturn, Protocol, TypeVar, Literal

if TYPE_CHECKING:
    from pathlib import Path

    from kivy._clock import ClockEvent
    from kivy.uix.screenmanager import ScreenManager

    from mindref.lib.adapters.atlas.fs.fs_atlas_repository import AtlasService
    from mindref.lib.adapters.editor.fs.fs_editor_repository import FileSystemEditor
    from mindref.lib.adapters.notes.android.android_note_repository import (
        AndroidNoteRepository,
    )
    from mindref.lib.adapters.notes.fs.fs_note_repository import (
        FileSystemNoteRepository,
    )
    from mindref.lib.plugins import PluginManager
    from mindref.lib.service.registry import Registry
    from mindref.lib.widgets import MindRefSettingsAndroid, MindRefSettingsNative


class AppRegistryProtocol(Protocol):
    atlas_service: AtlasService
    note_service: FileSystemNoteRepository | AndroidNoteRepository
    editor_service: FileSystemEditor
    plugin_manager: PluginManager
    registry: Registry

    platform_android: bool
    error_message: str
    screen_manager: ScreenManager
    fonts: dict[str, str]
    base_font_size: int
    colors: dict[str, tuple[float, float, float] | tuple[float, float, float, float]]
    settings_cls: str | MindRefSettingsAndroid | MindRefSettingsNative
    user_data_dir: str
    note_files: list[Path]

    def dispatch(self, *args, **kwargs) -> None: ...

    def select_index(self, value: int) -> None: ...

    def open_settings(self) -> None: ...

    def bind(self, **kwargs: Callable): ...

    def stop(self) -> NoReturn: ...

    def setter(self, prop: Literal["note_files"]) -> Callable: ...


T = TypeVar("T", bound=AppRegistryProtocol)
GetApp = Callable[[], T]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Path | None
    notes: list[Path]
