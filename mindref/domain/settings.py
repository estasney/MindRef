from pathlib import Path

from kivy import platform

SETTINGS_BEHAVIOR_PATH = Path(__file__).parent / "settings" / "app_settings.json"

from .plugin_settings import SETTINGS_PLUGIN_DATA as _SETTINGS_PLUGIN_DATA

_common_settings = [
    {"type": "title", "title": "Behavior"},
    {
        "type": "bool",
        "title": "Show New First",
        "desc": "Sort notes by date, newest first",
        "section": "Behavior",
        "key": "NEW_FIRST",
    },
    {
        "type": "string",
        "title": "Initial Category",
        "desc": "If set, skip the category selection screen and load this category when MindRef launches",
        "key": "CATEGORY_SELECTED",
        "section": "Behavior",
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
