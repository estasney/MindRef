import logging
import os
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING
from kivy.parser import parse_color
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)

from services.atlas.atlas import AtlasService
from services.backend.fileStorage.fileBackend import FileSystemBackend
from services.editor.fileStorage import FileSystemEditor
from services.settings import (
    SETTINGS_BEHAVIOR_PATH,
    SETTINGS_DISPLAY_PATH,
    SETTINGS_STORAGE_PATH,
)
from utils.registry import app_registry
from widgets.screens import NoteAppScreenManager

if TYPE_CHECKING:
    from services.backend.fileStorage.utils import CategoryFiles


class NoteAFly(App):
    APP_NAME = "NoteAFly"
    atlas_service = AtlasService(storage_path=Path("./static").resolve())
    note_service = FileSystemBackend(new_first=True)
    editor_service = FileSystemEditor()
    note_categories = ListProperty()
    note_category = StringProperty("")
    note_data = DictProperty(rebind=True)
    note_category_meta = ListProperty()
    next_note_scheduler = ObjectProperty()
    screen_transitions = OptionProperty(
        "slide", options=["None", "Slide", "Rise-In", "Card", "Fade", "Swap", "Wipe"]
    )
    menu_open = BooleanProperty(False)
    display_state = OptionProperty(
        "choose", options=["choose", "display", "list", "edit"]
    )
    play_state = OptionProperty("play", options=["play", "pause"])
    paginate_interval = NumericProperty(15)
    log_level = NumericProperty(logging.ERROR)

    screen_manager = ObjectProperty()
    fonts = DictProperty({"mono": "RobotoMono", "default": "Roboto"})
    base_font_size = NumericProperty()
    colors = DictProperty(
        {
            "White": (1, 1, 1),
            "Gray-100": parse_color("#f3f3f3"),
            "Gray-200": parse_color("#dddedf"),
            "Gray-300": parse_color("#c7c8ca"),
            "Gray-400": parse_color("#9a9da1"),  # White text
            "Gray-500": parse_color("#6d7278"),
            "Codespan": (0, 0, 0, 0.15),
            "Primary": parse_color("#37464f"),
            "Dark": parse_color("#101f27"),
            "Accent-One": parse_color("#388fe5"),
            "Accent-Two": parse_color("#56e39f"),
            "Warn": (
                0.9803921568627451,
                0.09803921568627451,
                0.09803921568627451,
                1.0,
            ),  # fa1919
        }
    )
    """
        Attributes
        ----------

        note_service: BackendProtocol
        note_categories: ListProperty
            All known note categories
        note_category: StringProperty
            The active Category. If no active category, value is empty string
        note_data: DictProperty
            The active Note belonging to active Category
        note_category_meta: ListProperty
            Metadata for notes associated with active Category. Info such as Title, and Shortcuts
        next_note_scheduler: ObjectProperty
        display_state: OptionProperty
            One of [Display, Choose]
            Choose:: Display all known categories
            Display:: Iterate through notes matching `self.note_category`
        play_state: OptionProperty
            One of [play, pause]
            play:: schedule pagination through notes
            pause:: stop pagination through notes
        screen_manager: ObjectProperty
            Holds the reference to ScreenManager
        colors: DictProperty
            Color scheme
        log_level: NumericProperty
        """

    def on_display_state(self, instance, new):
        if new != "list":
            return
        if new == "edit":
            self.play_state = "pause"
        if self.next_note_scheduler:
            self.next_note_scheduler.cancel()

    def select_index(self, value):
        def scheduled_select(dt, val):
            self.note_service.set_index(val)
            self.note_data = self.note_service.current_note().to_dict()
            self.play_state = "pause"
            self.display_state = "display"

        func = partial(scheduled_select, val=value)
        Clock.schedule_once(func)

    def paginate(self, value):
        self.next_note_scheduler.cancel()
        Clock.schedule_once(partial(self.paginate_note, direction=value), 0)
        if self.play_state == "play":
            self.next_note_scheduler()

    def toggle_play_state(self, *args, **kwargs):
        if self.play_state == "play":
            self.play_state = "pause"
        else:
            self.play_state = "play"

    def paginate_note(self, *args, **kwargs):
        direction = kwargs.get("direction", 1)
        is_initial = kwargs.get("initial", False)
        """Update `self.note_data` from `self.notes_data`"""
        if is_initial:
            self.note_data = self.note_service.current_note().to_dict()
        else:
            if direction > 0:
                self.note_data = self.note_service.next_note().to_dict()
            else:
                self.note_data = self.note_service.previous_note().to_dict()

    def on_log_level(self, instance, value):
        Logger.setLevel(int(value))

    def on_play_state(self, instance, value):
        if value == "pause":
            if self.next_note_scheduler:
                self.next_note_scheduler.cancel()
        else:
            self.next_note_scheduler()

    def on_note_category(self, instance, value: str):
        """
        Category button pressed
        """
        self.note_service.current_category = value

        def return_to_category(dt):
            self.note_category_meta = []
            if self.next_note_scheduler:
                self.next_note_scheduler.cancel()
            self.display_state = "choose"

        def select_category(dt, category):
            self.note_category_meta = self.note_service.category_meta
            if not self.next_note_scheduler:
                self.next_note_scheduler = Clock.schedule_interval(
                    self.paginate_note, self.paginate_interval
                )
            if self.play_state == "pause":
                self.next_note_scheduler.cancel()
            else:
                if self.play_state == "play":
                    self.next_note_scheduler()
            self.paginate_note(initial=True)
            self.display_state = "display"

        if not value:
            Clock.schedule_once(return_to_category)
            return
        else:
            func = partial(select_category, category=value)
            Clock.schedule_once(func)

    def on_note_data(self, *args, **kwargs):
        self.screen_manager.handle_notes(self)

    def note_files_listener(self, files: "CategoryFiles"):
        Logger.debug(f"Note Files from Registry {files}")
        self.note_categories = files

    def refresh_note_categories(self, *args):
        Logger.debug("Refreshing note categories")

        def clear_note_categories(dt):
            self.note_categories = []
            Clock.schedule_once(refresh_categories, 1)

        def refresh_categories(dt):
            self.note_service.refresh_categories()

        Clock.schedule_once(clear_note_categories)

    def build(self):
        storage_path = (
            np if (np := self.config.get("Storage", "NOTES_PATH")) != "None" else None
        )
        if storage_path:
            self.note_service.storage_path = storage_path
        self.note_service.new_first = (
            True if self.config.get("Behavior", "NEW_FIRST") == "True" else False
        )
        sm = NoteAppScreenManager(self)
        sm.screen_transitions = self.screen_transitions
        self.screen_manager = sm
        self.play_state = self.config.get("Behavior", "PLAY_STATE")
        self.note_category = self.config.get("Behavior", "CATEGORY_SELECTED")
        self.log_level = self.config.get("Behavior", "LOG_LEVEL")
        self.base_font_size = self.config.get("Display", "BASE_FONT_SIZE")
        if storage_path:
            self.note_categories = self.note_service.categories
        app_registry.note_files(self.note_files_listener)
        return sm

    def build_settings(self, settings):
        settings.add_json_panel("Storage", self.config, SETTINGS_STORAGE_PATH)
        settings.add_json_panel("Display", self.config, SETTINGS_DISPLAY_PATH)
        settings.add_json_panel("Behavior", self.config, SETTINGS_BEHAVIOR_PATH)

    def build_config(self, config):
        get_environ = os.environ.get
        config.setdefaults("Storage", {"NOTES_PATH": get_environ("NOTES_PATH", None)})
        config.setdefaults(
            "Display", {"BASE_FONT_SIZE": 16, "SCREEN_HEIGHT": 640, "SCREEN_WIDTH": 800}
        )
        config.setdefaults(
            "Behavior",
            {
                "NEW_FIRST": True,
                "PLAY_STATE": "play",
                "CATEGORY_SELECTED": "",
                "LOG_LEVEL": int(get_environ("LOG_LEVEL", logging.INFO)),
                "TRANSITIONS": "Slide",
            },
        )

    def on_config_change(self, config, section, key, value):
        if section == "Storage":
            if key == "NOTES_PATH":
                self.note_service.storage_path = value
                self.note_categories = self.note_service.categories
        elif section == "Behavior":
            if key == "LOG_LEVEL":
                self.log_level = value
            elif key == "NEW_FIRST":
                ...  # No effect here, this is on first load
            elif key == "PLAY_STATE":
                ...  # No effect here, this is on first load
            elif key == "TRANSITIONS":
                self.screen_transitions = value
        elif section == "Display":
            if key == "BASE_FONT_SIZE":
                self.base_font_size = value
            elif key == "SCREEN_WIDTH":
                Config.set("graphics", "width", value)
                Config.write()
            elif key == "SCREEN_HEIGHT":
                Config.set("graphics", "height", value)
                Config.write()


if __name__ == "__main__":
    NoteAFly().run()
