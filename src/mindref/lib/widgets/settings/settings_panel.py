from kivy import Logger
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.settings import SettingPath, SettingsWithSpinner

from mindref.lib.adapters_v2.brokered.android.android_file_system import (
    AndroidFileSystemAdapter,
)
from mindref.lib.utils import get_app
from mindref.lib.widgets.behavior.interact_behavior import InteractBehavior


class MindRefSettingsNative(InteractBehavior, SettingsWithSpinner):
    """
    Extends `SettingsWithSpinner` to fire the 'interact' event
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AndroidSettingPath(SettingPath):
    value = StringProperty()
    open_file_picker = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_app = get_app

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind("on_release", self._create_popup)

    def select_folder_callback(self, uri: str):
        Logger.info(f"Settings: selected {uri}")
        self.value = uri

    def _create_popup(self, *args):
        # TODO - "Popup Android File Picker"
        app = self.get_app()
        if self.open_file_picker is None:
            raise ValueError("open_file_picker is not set in the settings panel")
        self.open_file_picker(self.select_folder_callback)


class MindRefSettingsAndroid(SettingsWithSpinner):
    """
    Overrides FilePicker on Android to use DocumentProvider
    """

    storage_provider: AndroidFileSystemAdapter | None = ObjectProperty()

    __events__ = ("open_file_picker",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_open_file_picker(self, widget, value):
        """
        Event fired when the file picker is requested.
        """

        def update_widget_value_cb(val):
            widget.value = str(val)
            self.storage_provider.unregister_external_storage_callback()

        self.storage_provider.prompt_for_external_storage(
            on_complete=update_widget_value_cb
        )

    def create_json_panel(self, title, config, filename=None, data=None):
        self.register_type("android_path", AndroidSettingPath)
        return super().create_json_panel(title, config, filename, data)
