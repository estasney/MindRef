import json
from pathlib import Path
from platform import platform
from typing import Any

from kivy import Logger  # type:ignore
from kivy.app import App
from kivy.config import ConfigParser
from kivy.properties import (
    BooleanProperty,
    ConfigParserProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.settings import Settings

from mindref.lib.domain.settings import app_settings


def _to_path(value: str | Path | None) -> Path | None:
    if value in {"None", "null", "", None}:
        return None
    return Path(value)


class PathConfigParserProperty(ConfigParserProperty):
    # noinspection PyArgumentList
    def __init__(
        self, default: Path | None, section: str, key: str, config_name: str = "app"
    ):
        super().__init__(
            default, section, key, config_name, val_type=_to_path, errorvalue=None
        )

    def set(self, EventDispatcher_obj, value):
        val = "" if value is None else str(value)
        super().set(EventDispatcher_obj, val)


class SettingsMixin(App):
    storage_path: Path | None = PathConfigParserProperty(
        default=None, section="Storage", key="storage_path", config_name="app"
    )
    # noinspection PyArgumentList
    base_font_size: int = ConfigParserProperty(
        16, "Display", "base_font_size", "app", val_type=int, errorvalue=16
    )

    screen_manager: ObjectProperty
    platform_android: BooleanProperty

    def build_settings(self, settings: Settings):
        settings.add_json_panel(self.title, self.config, data=json.dumps(app_settings))

    def build_config(self, config: ConfigParser):
        match platform:  # We can't use self.platform_android yet
            case "android":
                config.setdefaults("Storage", {"storage_path": None})
                config.setdefaults("Display", {"base_font_size": 18})

            case _:
                config.setdefaults("Storage", {"storage_path": None})
                config.setdefaults("Display", {"base_font_size": 16})

    def open_settings(self, *largs):
        self.screen_manager.current = "settings_screen"
        super().open_settings(*largs)

    def close_settings(self, *largs):
        self.screen_manager.current = "main_screen"
        super().close_settings(*largs)
