from pathlib import Path

SETTINGS_BEHAVIOR_PATH = Path(__file__).parent / "settings" / "app_settings.json"

from .plugin_settings import SETTINGS_PLUGIN_DATA as _SETTINGS_PLUGIN_DATA

app_settings = [
    {"type": "title", "title": "Storage"},
    {
        "type": "path",
        "title": "Note Storage",
        "desc": "Directory containing note categories",
        "section": "Storage",
        "key": "NOTES_PATH",
    },
    {"type": "title", "title": "Behavior"},
    {
        "type": "bool",
        "title": "Show New First",
        "desc": "Sort notes by date, newest first",
        "section": "Behavior",
        "key": "NEW_FIRST",
    },
    {
        "type": "bool",
        "title": "Autoplay on Start",
        "desc": "Start MindRef with 'Play' enabled",
        "section": "Behavior",
        "key": "PLAY_STATE",
    },
    {
        "type": "numeric",
        "title": "Autoplay Speed",
        "desc": "When enabled, Autoplay, will wait this many seconds between notes",
        "key": "PLAY_DELAY",
        "section": "Behavior",
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
    {
        "type": "options",
        "title": "Screen Transitions",
        "desc": "Select screen transition animation",
        "key": "TRANSITIONS",
        "options": ["None", "Slide", "Rise-In", "Card", "Fade", "Swap", "Wipe"],
        "section": "Behavior",
    },
]

if _SETTINGS_PLUGIN_DATA:
    app_settings.extend(_SETTINGS_PLUGIN_DATA)
