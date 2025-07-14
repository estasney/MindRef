import json
from platform import platform
from typing import Any

from kivy import Logger  # type:ignore
from kivy.app import App
from kivy.config import ConfigParser
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty,
    NumericProperty,
)
from kivy.uix.settings import Settings

from mindref.lib.domain.settings import app_settings


class SettingsMixin(App):
    storage_path = StringProperty()
    screen_manager: ObjectProperty
    platform_android: BooleanProperty
    base_font_size = NumericProperty()

    def build_settings(self, settings: Settings):
        settings.add_json_panel(self.title, self.config, data=json.dumps(app_settings))

    def build_config(self, config: ConfigParser):
        match platform:  # We can't use self.platform_android yet
            case "android":
                config.setdefaults("Storage", {"NOTES_PATH": None})
                config.setdefaults("Display", {"BASE_FONT_SIZE": 18})

            case _:
                config.setdefaults(
                    "Storage",
                    {"NOTES_PATH": self.user_data_dir},
                )
                config.setdefaults("Display", {"BASE_FONT_SIZE": 16})

    def on_config_change(
        self, config: ConfigParser, section: str, key: str, value: Any
    ):
        truthy = {True, "1", "True"}
        Logger.info(f"{type(self).__name__}: on_config_change - {section},{key}")
        match section, key:
            case "Storage", "NOTES_PATH" if not self.platform_android:
                self.note_service.storage_path = value
                self.registry.set_note_storage_path(value)
                self.registry.query_all_v2()

            case "Storage", "NOTES_PATH" if self.platform_android:
                self.note_service.storage_path = value
                self.registry.set_note_storage_path(value)
                self.registry.query_all_v2()

            case "Display", "BASE_FONT_SIZE":
                self.base_font_size = int(value)

    def open_settings(self, *largs):
        self.screen_manager.current = "settings_screen"
        super().open_settings(*largs)

    def close_settings(self, *largs):
        self.screen_manager.current = "main_screen"
        super().close_settings(*largs)
