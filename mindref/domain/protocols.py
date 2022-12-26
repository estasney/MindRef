from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Protocol, TYPE_CHECKING, TypeVar, Union, NoReturn

from service.registry import Registry

if TYPE_CHECKING:
    from adapters.atlas.fs.fs_atlas_repository import AtlasService
    from adapters.editor.fs.fs_editor_repository import FileSystemEditor
    from adapters.notes.fs.fs_note_repository import FileSystemNoteRepository
    from adapters.notes.android.android_note_repository import AndroidNoteRepository
    from plugins import PluginManager
    from mindref.mindref import DISPLAY_STATES, DISPLAY_STATE, PLAY_STATE
    from kivy._clock import ClockEvent  # noqa
    from kivy.uix.screenmanager import ScreenManager
    from widgets import MindRefSettingsAndroid, MindRefSettingsNative


class AppRegistryProtocol(Protocol):
    atlas_service: "AtlasService"
    note_service: "Union[FileSystemNoteRepository, AndroidNoteRepository]"
    editor_service: "FileSystemEditor"
    plugin_manager: "PluginManager"
    registry: "Registry"

    platform_android: bool
    note_categories: list[str]
    note_category: str
    menu_open: bool
    display_state_last: "DISPLAY_STATES"
    display_state_current: "DISPLAY_STATES"
    display_state: "DISPLAY_STATE"
    play_state: "PLAY_STATE"
    error_message: str
    paginate_interval: int
    paginate_timer: "ClockEvent"
    screen_manager: "ScreenManager"
    fonts: dict[str, str]
    base_font_size: int
    colors: dict[str, tuple[float, float, float] | tuple[float, float, float, float]]
    settings_cls: str | "MindRefSettingsAndroid" | "MindRefSettingsNative"
    user_data_dir: str

    def dispatch(self, *args, **kwargs) -> None:
        ...

    def display_state_trigger(self, state: "DISPLAY_STATES") -> None:
        ...

    def play_state_trigger(self, state: "PLAY_STATE") -> None:
        ...

    def select_index(self, value: int) -> None:
        ...

    def open_settings(self) -> None:
        ...

    def bind(self, **kwargs: Callable):
        ...

    def stop(self) -> NoReturn:
        ...


T = TypeVar("T", bound=AppRegistryProtocol)
GetApp = Callable[[], T]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Optional[Path]
    notes: list[Path]
