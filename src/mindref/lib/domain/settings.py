from pathlib import Path
from typing import Literal

from kivy import platform

SETTINGS_BEHAVIOR_PATH = Path(__file__).parent / "settings" / "app_settings.json"
SortOptions = Literal["Creation Date", "Title", "Last Modified Date"]

_common_settings = [
    {"type": "title", "title": "Display"},
    {
        "type": "numeric",
        "title": "Base Font Size",
        "desc": "Set the base font size",
        "section": "Display",
        "key": "BASE_FONT_SIZE",
    },
]

_storage_settings = [
    {"type": "title", "title": "Storage"},
    {
        "type": "path",
        "title": "Note Storage",
        "desc": "Directory containing note categories",
        "section": "Storage",
        "key": "NOTES_PATH",
    },
]
_storage_settings_android = [
    {"type": "title", "title": "Storage"},
    {
        "type": "android_path",
        "title": "Note Storage",
        "desc": "Directory containing note categories",
        "section": "Storage",
        "key": "NOTES_PATH",
    },
]

match platform:
    case ("android", _):
        app_settings = [*_storage_settings_android, *_common_settings]
    case _:
        app_settings = [*_storage_settings, *_common_settings]
