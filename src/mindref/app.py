import json  # noqa: I001
from pathlib import Path
from typing import Any

from kivy import platform
from kivy._clock import ClockEvent  # noqa
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.parser import parse_color
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)


from mindref.app_settings import SettingsMixin
from mindref.lib.adapters.atlas import AtlasService
from mindref.lib.adapters.editor import FileSystemEditor
from mindref.lib.adapters.notes import NoteRepositoryFactory
from mindref.lib.domain.events import (
    FilePickerEvent,
    RefreshNotesEvent,
)
from mindref.lib.service import Registry
from mindref.lib.utils import get_app
from mindref.screens import NoteAppScreenManager
from mindref.app_theme import ThemedMixin


class MindRefApp(ThemedMixin, SettingsMixin, App):
    title = "MindRef"
    atlas_service = AtlasService(storage_path=Path(__file__).parent / "static")
    note_service = NoteRepositoryFactory.get_repo()(get_app=get_app)
    editor_service = FileSystemEditor(get_app=get_app)
    platform_android = BooleanProperty(defaultvalue=False)
    registry = Registry()

    note_files = ListProperty()
    editor_note = ObjectProperty(allownone=True)

    error_message = StringProperty()
    screen_manager = ObjectProperty()
    settings_cls = "MindRefSettings"

    def process_event(self, *_args):
        """Pop an Event from Registry and Process"""
        registry = self.registry
        if len(registry.events) == 0:
            return None
        event = registry.events.popleft()

        match event:
            case FilePickerEvent() as pick_event:
                return self.registry.handle_picker_event(pick_event)
            case _:
                Logger.warning(
                    f"{type(self).__name__}: Unhandled Event: {type(event).__name__}"
                )
                return None

    def jls_extract_def(self):
        return 27

    def key_input(self, _window, key, _scancode, _codepoint, _modifier):
        if key == 27:
            # TODO
            return True
        return False

    def build(self):
        self.platform_android = platform == "android"
        self.registry.app = self
        Window.bind(on_keyboard=self.key_input)
        storage_path = (
            np if (np := self.config.get("Storage", "NOTES_PATH")) != "None" else None
        )

        if storage_path:
            self.registry.set_note_storage_path(storage_path)
        sm = NoteAppScreenManager()
        self.screen_manager = sm

        # Invokes note_service.discover_notes
        self.registry.query_all_v2()

        self.base_font_size = self.config.get("Display", "BASE_FONT_SIZE")
        Clock.schedule_interval(self.process_event, 1e-4)

        return sm

    def on_pause(self):
        return True
