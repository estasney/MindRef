import json
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
from kivy.uix.settings import Settings

from mindref.lib.adapters.atlas import AtlasService
from mindref.lib.adapters.editor import FileSystemEditor
from mindref.lib.adapters.notes import NoteRepositoryFactory
from mindref.lib.domain.events import (
    FilePickerEvent,
    RefreshNotesEvent,
)
from mindref.lib.domain.settings import app_settings
from mindref.lib.service import Registry
from mindref.lib.utils import get_app
from mindref.screens import NoteAppScreenManager


class MindRefApp(App):
    title = "MindRef"
    atlas_service = AtlasService(storage_path=Path(__file__).parent / "static")
    note_service = NoteRepositoryFactory.get_repo()(get_app=get_app)
    editor_service = FileSystemEditor(get_app=get_app)
    platform_android = BooleanProperty(defaultvalue=False)
    registry = Registry()

    note_files = ListProperty()
    editor_note = ObjectProperty(allownone=True)

    menu_open = BooleanProperty(False)

    error_message = StringProperty()

    screen_manager = ObjectProperty()

    fonts = DictProperty({"mono": "RobotoMono", "default": "Roboto", "icons": "Icon"})
    base_font_size = NumericProperty()
    colors = DictProperty(
        {
            "White": (1, 1, 1),
            "Black": (0, 0, 0),
            "Gray-100": parse_color("#f5f5f5"),
            "Gray-200": parse_color("#dadbda"),
            "Gray-300": parse_color("#c1c1c1"),
            "Gray-400": parse_color("#a7a7a7"),
            "Gray-500": parse_color("#8f8f8f"),
            "Gray-600": parse_color("#777777"),
            "Gray-700": parse_color("#606060"),
            "Gray-800": parse_color("#4a4a4a"),
            "Gray-900": parse_color("#353535"),
            "Codespan": parse_color("#00000026"),
            "Keyboard": parse_color("#ffffffaf"),
            "KeyboardShadow": parse_color("#656565ff"),
            "Primary": parse_color("#37464f"),
            "Dark": parse_color("#1f1f1f"),
            "Accent-One": parse_color("#388fe5"),
            "Accent-Two": parse_color("#56e39f"),
            "Warn": parse_color("#fa1919"),
        }
    )
    """
        Attributes
        ----------

        note_service: AbstractNoteRepository
        note_categories: ListProperty
            All known note categories
        note_category: StringProperty
            The active Category. If no active category, value is empty string
        editor_note: ObjectProperty
            Ephemeral note used by editor service
        note_category_meta: ListProperty
            Metadata for notes associated with active Category. Info such as Title and index
        next_note_scheduler: ObjectProperty
        
        error_message: StringProperty
            Message 
        
        screen_manager: ObjectProperty
            Holds the reference to ScreenManager
        colors: DictProperty
            Color scheme
        log_level: NumericProperty
        """

    settings_cls = "MindRefSettings"

    def on_paginate(self, *args, **kwargs) -> None: ...

    def select_index(self, value: int):
        self.registry.set_note_index(value)

    def paginate_note(self, direction: int = 1):
        """
        Update our note_data, and the direction transition for our ScreenManager
        """

        return self.registry.paginate_note(direction)

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

    def key_input(self, _window, key, _scancode, _codepoint, _modifier):
        if key == 27:  # Esc Key
            # TODO
            return True
        return False

    """Kivy"""

    def build(self):
        # noinspection PyUnresolvedReferences
        self.register_event_type("on_paginate")
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

    def build_settings(self, settings: Settings):
        settings.add_json_panel("MindRef", self.config, data=json.dumps(app_settings))

    def build_config(self, config: Config):
        config.setdefaults(
            "Behavior",
            {
                "NOTE_SORTING": "Creation Date",
                "NOTE_SORTING_ASCENDING": False,
                "CATEGORY_SORTING": "Creation Date",
                "CATEGORY_SORTING_ASCENDING": False,
            },
        )

        match platform:  # We can't use self.platform_android yet
            case "android":
                config.setdefaults("Storage", {"NOTES_PATH": None})
                config.setdefaults("Display", {"BASE_FONT_SIZE": 18})
                config.setdefaults(
                    "Plugins", {"SCREEN_SAVER_ENABLE": False, "SCREEN_SAVER_DELAY": 60}
                )

            case _:
                config.setdefaults(
                    "Storage",
                    {"NOTES_PATH": self.user_data_dir},
                )
                config.setdefaults("Display", {"BASE_FONT_SIZE": 16})
                config.setdefaults(
                    "Plugins", {"SCREEN_SAVER_ENABLE": False, "SCREEN_SAVER_DELAY": 60}
                )

    def on_config_change(self, config: Config, section: str, key: str, value: Any):
        truthy = {True, "1", "True"}
        Logger.info(f"{type(self).__name__}: on_config_change - {section},{key}")
        match section, key:
            case "Storage", "NOTES_PATH" if not self.platform_android:
                self.note_service.storage_path = value

                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Storage", "NOTES_PATH" if self.platform_android:
                self.registry.set_note_storage_path(value)

                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "NOTE_SORTING":
                self.note_service.note_sorting = value

                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "NOTE_SORTING_ASCENDING":
                self.note_service.note_sorting_ascending = (
                    value if value in truthy else False
                )

                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "CATEGORY_SORTING":
                self.note_service.category_sorting = value

                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Behavior", "CATEGORY_SORTING_ASCENDING":
                self.note_service.category_sorting_ascending = (
                    value if value in truthy else False
                )

                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            case "Display", "BASE_FONT_SIZE":
                self.base_font_size = int(value)
            case "Plugins", _:
                ...

    def on_pause(self):
        return True
