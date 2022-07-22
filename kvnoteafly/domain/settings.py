from pathlib import Path

SETTINGS_STORAGE_PATH = Path(__file__).parent / "settings" / "storage.json"
SETTINGS_DISPLAY_PATH = Path(__file__).parent / "settings" / "display.json"
SETTINGS_BEHAVIOR_PATH = Path(__file__).parent / "settings" / "behavior.json"

from .plugin_settings import SETTINGS_PLUGIN_DATA
