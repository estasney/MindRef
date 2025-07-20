from kivy.uix.settings import SettingsWithNoMenu

from . import SettingsAndroidPath


class MindrefSettings(SettingsWithNoMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_type("android_path", SettingsAndroidPath)
