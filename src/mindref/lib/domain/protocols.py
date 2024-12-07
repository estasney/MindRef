from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, NoReturn, Protocol, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from kivy._clock import ClockEvent
    from kivy.uix.screenmanager import ScreenManager

    from mindref.lib import DisplayState
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
    note_categories: list[str]
    note_category: str
    menu_open: bool
    display_state_last: DisplayState
    display_state_current: DisplayState
    display_state: DisplayState

    error_message: str
    paginate_interval: int
    paginate_timer: ClockEvent
    screen_manager: ScreenManager
    fonts: dict[str, str]
    base_font_size: int
    colors: dict[str, tuple[float, float, float] | tuple[float, float, float, float]]
    settings_cls: str | MindRefSettingsAndroid | MindRefSettingsNative
    user_data_dir: str

    def dispatch(self, *args, **kwargs) -> None: ...

    def display_state_trigger(self, state: DisplayState) -> None: ...

    def select_index(self, value: int) -> None: ...

    def open_settings(self) -> None: ...

    def bind(self, **kwargs: Callable): ...

    def stop(self) -> NoReturn: ...


T = TypeVar("T", bound=AppRegistryProtocol)
GetApp = Callable[[], T]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Path | None
    notes: list[Path]
