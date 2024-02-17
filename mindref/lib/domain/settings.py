from pathlib import Path
from typing import Literal

from kivy import platform
from .plugin_settings import SETTINGS_PLUGIN_DATA as _SETTINGS_PLUGIN_DATA

SETTINGS_BEHAVIOR_PATH = Path(__file__).parent / "settings" / "app_settings.json"
SortOptions = Literal["Creation Date", "Title", "Last Modified Date"]

_common_settings = [
    {"type": "title", "title": "Behavior"},
    {
        "type": "options",
        "title": "Note Sorting",
        "desc": "How to sort notes",
        "section": "Behavior",
        "key": "NOTE_SORTING",
        "options": ["Creation Date", "Title", "Last Modified Date"],
    },
    {
        "type": "bool",
        "title": "Ascending Note Sorting",
        "desc": "Flips the sorting order of notes",
        "section": "Behavior",
        "key": "NOTE_SORTING_ASCENDING",
    },
    {
        "type": "options",
        "title": "Category Sorting",
        "desc": "How to sort categories",
        "section": "Behavior",
        "key": "CATEGORY_SORTING",
        "options": ["Creation Date", "Title", "Last Modified Date"],
    },
    {
        "type": "bool",
        "title": "Ascending Category Sorting",
        "desc": "Flips the sorting order of categories",
        "section": "Behavior",
        "key": "CATEGORY_SORTING_ASCENDING",
    },
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

match (platform, _SETTINGS_PLUGIN_DATA):
    case ("android", _):
        app_settings = [*_storage_settings_android, *_common_settings]
    case (_, None):
        app_settings = [*_storage_settings, *_common_settings]
    case (_, list()):
        app_settings = [*_storage_settings, *_common_settings, *_SETTINGS_PLUGIN_DATA]
    case _:
        raise AssertionError(f"Unhandled settings {platform} {_SETTINGS_PLUGIN_DATA}")
