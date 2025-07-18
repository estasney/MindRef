import json
from pathlib import Path

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
    android_storage_path: str = ConfigParserProperty(
        "",
        "Storage",
        "android_storage_path",
        "app",
    )

    # noinspection PyArgumentList
    base_font_size: int = ConfigParserProperty(
        16, "Display", "base_font_size", "app", val_type=int, errorvalue=16
    )

    screen_manager: ObjectProperty
    platform_android: bool
    fs: DirectFileSystemAdapter | AndroidFileSystemAdapter

    def _create_settings_native(self): ...

    def _create_settings_android(self):
        fs = self.fs
        if not isinstance(fs, AndroidFileSystemAdapter):
            raise TypeError(
                f"Expected AndroidFileSystemAdapter, got {type(fs).__name__}"
            )
        fs.prompt_for_external_storage

    def create_settings(self):
        settings = (
            self._create_settings_android()
            if self.platform_android
            else self._create_settings_native()
        )

    def build_settings(self, settings: Settings):
        settings_data = (
            get_android_settings() if self.platform_android else get_native_settings()
        )
        settings.add_json_panel(self.title, self.config, data=json.dumps(settings_data))

    def build_config(self, config: ConfigParser):
        if self.platform_android:
            config.setdefaults(
                "Storage",
                {
                    "android_storage_path": "",
                    "storage_path": Path(get_app().user_data_dir) / "notes",
                },
            )
            config.setdefaults("Display", {"base_font_size": 18})
        else:
            config.setdefaults("Storage", {"storage_path": None})
            config.setdefaults("Display", {"base_font_size": 16})

    def open_settings(self, *largs):
        self.screen_manager.current = "settings_screen"
        super().open_settings(*largs)

    def close_settings(self, *largs):
        self.screen_manager.current = "main_screen"
        super().close_settings(*largs)
