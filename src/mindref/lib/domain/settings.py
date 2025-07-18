from kivy import platform

_common_settings = [
    {"type": "title", "title": "Display"},
    {
        "type": "numeric",
        "title": "Base Font Size",
        "desc": "Set the base font size",
        "section": "Display",
        "key": "base_font_size",
    },
]

_storage_settings = [
    {"type": "title", "title": "Storage"},
    {
        "type": "path",
        "title": "Note Storage",
        "desc": "Root directory to read and store note files",
        "section": "Storage",
        "key": "storage_path",
    },
]
_storage_settings_android = [
    {"type": "title", "title": "Storage"},
    {
        "type": "android_path",
        "title": "Note Storage",
        "desc": "Root directory to read and store note files on your Android Device",
        "section": "Storage",
        "key": "android_storage_path",
    },
]


def get_native_settings():
    """Get the app settings based on the platform."""
    return [*_storage_settings, *_common_settings]


def get_android_settings():
    """Get the app settings for Android platform."""
    return [*_storage_settings_android, *_common_settings]
