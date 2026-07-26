from kivy.uix.settings import SettingsWithSpinner

from mindref.lib.widgets.settings.settings_android_path import SettingsAndroidPath


class MindrefSettings(SettingsWithSpinner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_type("android_path", SettingsAndroidPath)
