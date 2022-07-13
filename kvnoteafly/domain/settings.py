from pathlib import Path
import platform
import json

SETTINGS_STORAGE_PATH = Path(__file__).parent / "settings" / "storage.json"
SETTINGS_DISPLAY_PATH = Path(__file__).parent / "settings" / "display.json"
SETTINGS_BEHAVIOR_PATH = Path(__file__).parent / "settings" / "behavior.json"

#
# def generate_plugin_json() -> str:
#     data = []
#     if platform.node() == 'raspberrypi':
#         data.append(dict(type="bool", title="ScreenSaver", desc="Enable a ScreenSaver",
#                          section="Plugins", key="SCREEN_SAVER_ENABLE"
#                          ))
#         data.append(dict(type="numeric", title="ScreenSaver Delay", desc="Enable ScreenSaver after this many minutes",
#                          section="Plugins", key="SCREEN_SAVER_DELAY"
#                          ))
#     if not data:
#         data.append(dict(type="title", title="No Plugins Available"))
#     return json.dumps(data)


def generate_plugin_json() -> str:
    data = []

    data.append(
        dict(
            type="bool",
            title="ScreenSaver",
            desc="Enable a ScreenSaver",
            section="Plugins",
            key="SCREEN_SAVER_ENABLE",
        )
    )
    data.append(
        dict(
            type="numeric",
            title="ScreenSaver Delay",
            desc="Enable ScreenSaver after this many minutes",
            section="Plugins",
            key="SCREEN_SAVER_DELAY",
        )
    )

    return json.dumps(data)


SETTINGS_PLUGIN_DATA = generate_plugin_json()
