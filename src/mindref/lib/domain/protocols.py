from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures.thread import ThreadPoolExecutor
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from kivy.properties import (
        BooleanProperty,
        ConfigParserProperty,
        DictProperty,
        ListProperty,
        ObjectProperty,
        StringProperty,
    )
    from kivy.uix.screenmanager import ScreenManager

    from mindref.app_notes import NoteFile
    from mindref.lib.adapters.atlas.fs.fs_atlas_repository import AtlasService
    from mindref.lib.adapters.base import FileSystemBase
    from mindref.lib.widgets.settings.settings_mindref import MindrefSettings


class AppRegistryProtocol(Protocol):
    atlas_service: AtlasService
    fs: FileSystemBase
    platform_android: BooleanProperty
    error_message: StringProperty[str]
    screen_manager: ObjectProperty[ScreenManager]
    fonts: DictProperty[str, str]
    base_font_size: ConfigParserProperty[int]
    colors: DictProperty[str, Sequence[float]]
    settings_cls: ObjectProperty[type[MindrefSettings]]
    pool: ThreadPoolExecutor
    note_files: ListProperty[NoteFile]

    @property
    def user_data_dir(self) -> str: ...

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
