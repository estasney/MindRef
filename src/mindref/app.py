from __future__ import annotations

import json
from concurrent.futures import Future
from pathlib import Path
from typing import TypedDict, Unpack

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.config import ConfigParser
from kivy.core.window import Window, WindowBase
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    ConfigParserProperty,
    DictProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.settings import Settings as KivySettings
from kivy.utils import platform

from mindref.app_notes import NoteFile
from mindref.app_pool import get_pool
from mindref.app_settings import PathConfigParserProperty
from mindref.app_theme import THEME_COLORS
from mindref.lib.adapters import FileManager
from mindref.lib.adapters.atlas.fs.fs_atlas_repository import AtlasService
from mindref.lib.utils import get_app, required
from mindref.lib.widgets.settings.settings_mindref import MindrefSettings
from mindref.screens import NoteAppScreenManager


class MindRefInitKwargs(TypedDict, total=False):
    platform_android: bool


class MindRefApp(App):
    title = StringProperty("MindRef")
    atlas_service = AtlasService(storage_path=Path(__file__).parent / "static")
    settings_cls = ObjectProperty(MindrefSettings)

    platform_android = BooleanProperty(defaultvalue=False)
    enable_profiling = BooleanProperty(defaultvalue=False)
    note_files: ListProperty[NoteFile] = ListProperty(force_dispatch=True)
    editing_note: ObjectProperty[NoteFile | None] = ObjectProperty(allownone=True)
    error_message = StringProperty()
    screen_manager: ObjectProperty[NoteAppScreenManager] = ObjectProperty()

    storage_path = PathConfigParserProperty(
        default=None, section="Storage", key="storage_path", config_name="app"
    )
    external_storage_path = ConfigParserProperty(
        "",
        "Storage",
        "external_storage_path",
        "app",
    )

    fonts = DictProperty(
        {"mono": "JetBrainsMono", "default": "Roboto", "icons": "Icon"}
    )
    colors = DictProperty(THEME_COLORS)

    base_font_size = ConfigParserProperty(
        16, "Display", "base_font_size", "app", val_type=int, errorvalue=16
    )

    def __init__(self, **kwargs: Unpack[MindRefInitKwargs]):
        platform_android = kwargs.pop("platform_android", False)
        self.pool = get_pool()
        super().__init__(**kwargs)
        self.platform_android = platform_android
        self.fs = FileManager()
        self.bind(
            external_storage_path=lambda *_: setattr(
                self.fs, "external_storage_path", self.external_storage_path
            )
        )

    def on_platform_android(self, _instance: MindRefApp, value: bool) -> None:
        Logger.info(f"Platform changed: Android={value}")
        if self.platform_android:
            self.storage_path = Path(get_app().user_data_dir) / "notes"
            from mindref.lib.adapters.brokered.android.window_insets import (
                apply_window_insets,
            )

            apply_window_insets()

    def refresh_note_files(self, *_args: object) -> None:
        if self.storage_path is None:
            Logger.warning(
                f"{self.__class__.__name__} : storage_path is not set. "
                "Set it in Settings to load notes."
            )
            return
        self.screen_manager.dispatch("on_refresh", self, True, to_children=True)
        fut = self.pool.submit(
            self.fs.refresh_note_files, self.storage_path, self.external_storage_path
        )

        @mainthread
        def callback(future: Future[list[NoteFile]]):
            res = future.result()
            Logger.info(
                f"{self.__class__.__name__} : Note files successfully queried: {len(res)} files found."
            )
            self.note_files = res
            self.screen_manager.dispatch("on_refresh", self, False, to_children=True)

        fut.add_done_callback(callback)

    def read_note(self, note_id: str) -> str:
        """Read the contents of the note"""
        return self.fs.read_note(note_id=note_id, note_files=self.note_files)

    def edit_note(self, note_id: str) -> None:
        matched_note = next(
            (note for note in self.note_files if note.id == note_id), None
        )
        if matched_note is None:
            Logger.error(
                f"[{self.__class__.__name__}] Note with ID {note_id} not found."
            )
            return
        Logger.info(
            f"[{self.__class__.__name__}] Editing note: {matched_note.file_path}"
        )
        self.editing_note = matched_note
        self.screen_manager.current = "edit_screen"

    def cancel_edit_note(self, *_args: object) -> None:
        self.screen_manager.current = "main_screen"
        self.editing_note = None

    def save_edit_note(self, text: str) -> None:
        if not self.editing_note:
            Logger.error(
                f"[{self.__class__.__name__}] No note is currently being edited."
            )
            return

        storage_path = required(self.storage_path, "storage_path not set")
        edit_file_name = str(self.editing_note.file_path.relative_to(storage_path))
        self.fs.save_edit_note(
            storage_path=storage_path,
            external_storage_path=self.external_storage_path,
            file_name=edit_file_name,
            text=text,
        )
        self.refresh_note_files()
        Clock.schedule_once(self.cancel_edit_note)

    def draft_note(self):
        self.screen_manager.current = "draft_screen"

    def cancel_draft_note(self):
        self.screen_manager.current = "main_screen"

    def save_draft_note(self, file_name: str, text: str) -> None:
        storage_path = required(
            self.storage_path, "Cannot save a draft note without a storage_path"
        )
        draft_note_file = self.fs.save_draft_note(
            storage_path=storage_path,
            external_storage_path=self.external_storage_path,
            file_name=file_name,
            text=text,
        )

        note_files = [draft_note_file, *self.note_files]
        self.note_files = note_files
        self.screen_manager.current = "main_screen"

    def key_input(
        self,
        _window: WindowBase,
        key: int,
        _scancode: int,
        _codepoint: str,
        _modifier: list[str],
    ) -> bool:
        if key == 27:
            # TODO - Close nav drawer? Something else?
            return True
        return False

    def build(self):
        self.platform_android = platform == "android"
        Logger.info(f"Platform: {platform}, Android: {self.platform_android}")

        # Window.bind(on_keyboard=self.key_input)
        self.screen_manager = NoteAppScreenManager()
        self.bind(storage_path=lambda *_: self.refresh_note_files())
        Clock.schedule_once(lambda _: self.refresh_note_files())
        return self.screen_manager

    def build_settings(self, settings: KivySettings) -> None:
        settings_data = [
            {
                "type": "numeric",
                "title": "Base Font Size",
                "desc": "The base font size for the application.",
                "section": "Display",
                "key": "base_font_size",
            },
        ]
        if self.platform_android:
            settings_data.append(
                {
                    "type": "android_path",
                    "title": "External Storage Path",
                    "desc": "The path to the external storage directory.",
                    "section": "Storage",
                    "key": "external_storage_path",
                }
            )
        else:
            settings_data.append(
                {
                    "type": "path",
                    "title": "Storage Path",
                    "desc": "The path to the storage directory.",
                    "section": "Storage",
                    "key": "storage_path",
                }
            )
        settings.add_json_panel("MindRef", self.config, data=json.dumps(settings_data))

    def on_config_change(
        self, config: ConfigParser, section: str, key: str, value: str
    ) -> None:
        super().on_config_change(config, section, key, value)
        if section == "Storage":
            if key == "external_storage_path":
                self.external_storage_path = value
                Logger.info(
                    f"{self.__class__.__name__} : External storage path set to: {value}"
                )
            elif key == "storage_path":
                self.storage_path = Path(value)
                Logger.info(f"Storage path set to: {self.storage_path}")
        elif section == "Display" and key == "base_font_size":
            self.base_font_size = int(value)
            Logger.info(f"Base font size set to: {self.base_font_size}")

    def build_config(self, config: ConfigParser) -> None:
        if self.platform_android:
            config.setdefaults(
                "Storage",
                {
                    "external_storage_path": "",
                    "storage_path": Path(get_app().user_data_dir) / "notes",
                },
            )
            config.setdefaults("Display", {"base_font_size": 16})
        else:
            config.setdefaults("Storage", {"storage_path": None})
            config.setdefaults("Display", {"base_font_size": 16})

    def open_settings(self, *largs: object) -> bool:
        return super().open_settings(*largs)

    def close_settings(self, *largs: object) -> None:
        super().close_settings(*largs)

    def on_pause(self):
        return True

    def on_resume(self):
        Logger.info("On resume called, ensuring FBO is updated.")
        for ts in (0.01, 0.05, 0.2, 2.0):
            Clock.schedule_once(lambda _dt: Window.canvas.ask_update(), ts)
