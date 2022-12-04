from kivy import Logger, platform
from kivy.factory import Factory
from kivy.properties import StringProperty
from kivy.uix.settings import SettingPath, SettingsWithSpinner
from kivy.app import App

from domain.events import PromptExternalStorageAndroid
from widgets.behavior.interact_behavior import InteractBehavior
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.protocols import AppRegistryProtocol


class MindRefSettingsNative(InteractBehavior, SettingsWithSpinner):
    """
    Extends `SettingsWithSpinner` to fire the 'interact' event
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AndroidSettingPath(SettingPath):
    value = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_app = App.get_running_app

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind("on_release", self._create_popup)

    def select_folder_callback(self, uri: str):
        Logger.info(f"Settings: selected {uri}")
        self.value = uri

    def _create_popup(self, *args):
        app: "AppRegistryProtocol" = self.get_app()
        app.registry.push_event(
            PromptExternalStorageAndroid(on_complete=self.select_folder_callback)
        )


class MindRefSettingsAndroid(InteractBehavior, SettingsWithSpinner):
    """
    Overrides FilePicker on Android to use DocumentProvider
    """

    ...

    def __init__(self, *args, **kwargs):
        super(MindRefSettingsAndroid, self).__init__(*args, **kwargs)
        # override type

    def create_json_panel(self, title, config, filename=None, data=None):
        self.register_type("android_path", AndroidSettingPath)
        return super(MindRefSettingsAndroid, self).create_json_panel(
            title, config, filename, data
        )


match platform:
    case "android":
        Factory.register("MindRefSettings", cls=MindRefSettingsAndroid)
    case _:
        Factory.register("MindRefSettings", cls=MindRefSettingsNative)
