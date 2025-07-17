from pathlib import Path

from kivy import platform
from kivy._clock import ClockEvent  # noqa
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty,
)

from mindref.app_notes import AppNotesMixin
from mindref.app_settings import SettingsMixin
from mindref.app_theme import ThemedMixin
from mindref.lib.adapters.atlas import AtlasService
from mindref.screens import NoteAppScreenManager


class MindRefApp(ThemedMixin, SettingsMixin, AppNotesMixin, App):
    title = "MindRef"
    atlas_service = AtlasService(storage_path=Path(__file__).parent / "static")
    platform_android = BooleanProperty(defaultvalue=False)

    error_message = StringProperty()
    screen_manager = ObjectProperty()
    settings_cls = "MindRefSettings"
    storage_path: Path | None

    def key_input(self, _window, key, _scancode, _codepoint, _modifier):
        if key == 27:
            # TODO
            return True
        return False

    def build(self):
        self.platform_android = platform == "android"
        Window.bind(on_keyboard=self.key_input)
        self.screen_manager = NoteAppScreenManager()
        self.bind(storage_path=lambda *_: self.load_note_files())
        Clock.schedule_once(lambda _: self.load_note_files(), 0.5)
        return self.screen_manager

    def on_pause(self):
        return True
