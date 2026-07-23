from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from kivy.properties import DictProperty

from mindref.lib.adapters.base import FileSystemBase

if TYPE_CHECKING:
    from kivy.uix.screenmanager import ScreenManager

    from mindref.app_notes import NoteFile


class AppSettingsProtocol(Protocol):
    storage_path: Path | None
    external_storage_path: str
    base_font_size: int
    screen_manager: object
    platform_android: bool
    fs: FileSystemBase


class AppThemeProtocol(Protocol):
    fonts: DictProperty
    colors: DictProperty


class AppNotesProtocol(Protocol):
    storage_path: Path | None
    note_files: list["NoteFile"]  # Should be NoteFile type
    editing_note: list["NoteFile"]
    screen_manager: "ScreenManager"  # Should be ScreenManager type
    external_storage_path: str
    fs: FileSystemBase
