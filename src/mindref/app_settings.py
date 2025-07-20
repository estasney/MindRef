import json
from pathlib import Path

from kivy import Logger
from kivy.app import App
from kivy.config import ConfigParser
from kivy.properties import (
    ConfigParserProperty,
    ObjectProperty,
)
from kivy.uix.settings import Settings

from mindref.lib import get_app
from mindref.lib.adapters_v2 import FileSystemBase
from mindref.lib.adapters_v2.brokered.android.android_file_system import (
    AndroidFileSystemAdapter,
)
from mindref.lib.adapters_v2.direct_file_system import DirectFileSystemAdapter
from mindref.lib.domain.settings import get_android_settings, get_native_settings
from mindref.lib.widgets.settings.settings_mindref import MindrefSettings


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
    settings_cls = ObjectProperty(MindrefSettings)
    storage_path: Path | None = PathConfigParserProperty(
        default=None, section="Storage", key="storage_path", config_name="app"
    )
    external_storage_path: str = ConfigParserProperty(
        "",
        "Storage",
        "external_storage_path",
        "app",
    )

    # noinspection PyArgumentList
    base_font_size: int = ConfigParserProperty(
        16, "Display", "base_font_size", "app", val_type=int, errorvalue=16
    )

    screen_manager: ObjectProperty
    platform_android: bool
    fs: DirectFileSystemAdapter | AndroidFileSystemAdapter

    def on_platform_android(self, instance, value):
        Logger.info(f"Platform changed: Android={value}")
        if value:
            self.fs = AndroidFileSystemAdapter()
            self.fs.external_storage_path = self.external_storage_path
            self.bind(
                external_storage_path=lambda *_: setattr(
                    self.fs, "external_storage_path", self.external_storage_path
                )
            )
        else:
            self.fs = DirectFileSystemAdapter()

    def build_settings(self, settings):
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

    def build_config(self, config: ConfigParser):
        if self.platform_android:
            config.setdefaults(
                "Storage",
                {
                    "external_storage_path": "",
                    "storage_path": Path(get_app().user_data_dir) / "notes",
                },
            )
            config.setdefaults("Display", {"base_font_size": 18})
        else:
            config.setdefaults("Storage", {"storage_path": None})
            config.setdefaults("Display", {"base_font_size": 16})

    def open_settings(self, *largs):
        # self.screen_manager.current = "settings_screen"
        # super().open_settings(*largs)
        super().open_settings(*largs)

    def close_settings(self, *largs):
        # self.screen_manager.current = "main_screen"
        # super().close_settings(*largs)
        super().close_settings(*largs)
