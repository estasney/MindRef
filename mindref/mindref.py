import json
import logging
import os
from functools import partial
from pathlib import Path
from typing import Callable, Literal

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
    OptionProperty,
    StringProperty,
)

from adapters.atlas.fs.fs_atlas_repository import AtlasService
from adapters.editor.fs.fs_editor_repository import FileSystemEditor
from adapters.notes.fs.fs_note_repository import FileSystemNoteRepository
from domain.events import (
    AddNoteEvent,
    BackButtonEvent,
    CancelEditEvent,
    DiscoverCategoryEvent,
    EditNoteEvent,
    NoteCategoryEvent,
    NoteCategoryFailureEvent,
    NoteFetchedEvent,
    NotesQueryEvent,
    NotesQueryFailureEvent,
    RefreshNotesEvent,
    SaveNoteEvent,
)

from domain.settings import app_settings
from plugins import PluginManager
from service.registry import Registry
from utils import sch_cb
from utils.triggers import trigger_factory
from widgets.screens import NoteAppScreenManager


class MindRefApp(App):
    APP_NAME = "MindRef"
    atlas_service = AtlasService(storage_path=Path("./static").resolve())
    note_service = FileSystemNoteRepository(get_app=App.get_running_app, new_first=True)
    editor_service = FileSystemEditor(get_app=App.get_running_app)
    plugin_manager = PluginManager()

    registry = Registry(logger=Logger)

    note_categories = ListProperty()
    note_category = StringProperty("")
    note_data = DictProperty(rebind=True)

    editor_note = ObjectProperty(allownone=True)

    note_category_meta = ListProperty()
    next_note_scheduler = ObjectProperty()
    screen_transitions = OptionProperty(
        "slide", options=["None", "Slide", "Rise-In", "Card", "Fade", "Swap", "Wipe"]
    )
    menu_open = BooleanProperty(False)

    display_state = OptionProperty(
        "choose", options=["choose", "display", "list", "edit", "add", "error"]
    )
    display_state_trigger: Callable[
        [Literal["choose", "display", "list", "edit", "add"]], None
    ]
    error_message = StringProperty()
    play_state = OptionProperty("play", options=["play", "pause"])
    play_state_trigger: Callable[[Literal["play", "pause"]], None]

    paginate_interval = NumericProperty(15)

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

        note_service: AbstractNoteRepository
        note_categories: ListProperty
            All known note categories
        note_category: StringProperty
            The active Category. If no active category, value is empty string
        note_data: DictProperty
            The active Note belonging to active Category
        editor_note: ObjectProperty
            Ephemeral note used by editor service
        note_category_meta: ListProperty
            Metadata for notes associated with active Category. Info such as Title, and Shortcuts
        next_note_scheduler: ObjectProperty
        display_state: OptionProperty
            One of ["choose", "display", "list", "edit", "add", "error"]
                - choose: Display all known categories
                - display: Iterate through notes matching `self.note_category`
                - list: show a listing of notes in self.note_category
                - edit: Open an editor for current note
                - add: Open an editor for a new note
                - error: Show an error screen
        error_message: StringProperty
            Message 
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

    settings_cls = "MindRefSettings"

    def on_display_state(self, instance, new):

        if new in {"edit", "add"}:
            self.play_state_trigger("pause")
        if new == "edit":
            self.editor_note = self.editor_service.edit_current_note()
        elif new == "add":
            self.editor_note = self.editor_service.new_note(
                category=self.note_category, idx=self.note_service.index_size()
            )
        if self.next_note_scheduler:
            self.next_note_scheduler.cancel()

    def select_index(self, value):

        set_index = lambda x: self.note_service.set_index(value)
        set_note_data = lambda x: setattr(
            self, "note_data", self.note_service.current_note().to_dict()
        )
        pause_state = lambda x: self.play_state_trigger("pause")
        display_state_display = lambda x: self.display_state_trigger("display")

        sch_cb(0, set_index, set_note_data, pause_state, display_state_display)

    def paginate(self, value):
        self.next_note_scheduler.cancel()
        Clock.schedule_once(partial(self.paginate_note, direction=value), 0)
        if self.play_state == "play":
            self.next_note_scheduler()

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
        Category button pressed, or we're loading straight to category at launch
        """

        self.registry.set_note_category(self.note_category, on_complete=None)

    """
    Event Handlers for Registry
    """

    def process_cancel_edit_event(self, event: CancelEditEvent):

        clear_edit_note = lambda x: setattr(self, "editor_note", None)
        sch_cb(0, lambda x: self.display_state_trigger("display"), clear_edit_note)

    def process_edit_note_event(self, event: EditNoteEvent):
        data_note = self.registry.edit_note(category=event.category, idx=event.idx)
        update_edit_note = lambda x: setattr(self, "editor_note", data_note)
        update_display_state = lambda x: self.display_state_trigger("edit")
        sch_cb(0, update_edit_note, update_display_state)

    def process_add_note_event(self, event: AddNoteEvent):
        data_note = self.registry.new_note(category=self.note_category, idx=None)
        update_edit_note = lambda x: setattr(self, "editor_note", data_note)
        update_display_mode = lambda x: self.display_state_trigger("add")
        sch_cb(0, update_edit_note, update_display_mode)

    def process_save_note_event(self, event: SaveNoteEvent):
        note_is_new = self.display_state == "add"
        data_note = self.editor_note
        data_note.edit_text = event.text
        if note_is_new:
            data_note.edit_title = event.title
        update_edit_note = lambda x: setattr(self, "editor_note", None)
        update_display_state = lambda x: self.display_state_trigger("display")
        persist_note = lambda x: self.registry.save_note(data_note)
        sch_cb(1, update_display_state, persist_note, update_edit_note)

    def process_note_fetched_event(self, event: NoteFetchedEvent):
        note_data = event.note.to_dict()
        update_data = lambda x: setattr(self, "note_data", note_data)
        sch_cb(1, update_data)

    def process_refresh_notes_event(self, event: RefreshNotesEvent):
        clear_categories = lambda x: setattr(self, "note_categories", [])
        run_query = lambda x: self.registry.query_all(on_complete=event.on_complete)
        sch_cb(0.5, clear_categories, run_query)

    def process_note_category_event(self, event: NoteCategoryEvent):
        """Note Category has been set"""

        def return_to_category(dt):
            self.note_category_meta = []
            if self.next_note_scheduler:
                self.next_note_scheduler.cancel()
            self.display_state_trigger("choose")

        if not event.value:
            sch_cb(0.1, return_to_category)
            return

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

        sch_cb(0.1, partial(select_category, category=event.value))

    def process_note_category_failure_event(self, event: NoteCategoryFailureEvent):
        """Failed to set"""
        Logger.error(event)
        if self.config.get("Behavior", "CATEGORY_SELECTED") == event.value:
            # Clear the config
            app_config = Config.get_configparser("app")
            app_config.set("Behavior", "CATEGORY_SELECTED", "")
            app_config.write()

        if self.next_note_scheduler:
            self.next_note_scheduler.cancel()
        self.note_category = ""

    def process_notes_query_event(self, event: NotesQueryEvent):
        """Notes have finished Querying"""

        if event.on_complete is not None:
            sch_cb(0.1, event.on_complete)

    def process_notes_query_failure_event(self, event: NotesQueryFailureEvent):

        if event.on_complete is not None:
            sch_cb(0, event.on_complete)

        if event.error in ("permission_error", "not_found"):
            # Clear the bad entry from config
            self.note_service.storage_path = None
            app_config = Config.get_configparser("app")
            # If android we have a special homedir available with NOTES_PATH
            app_config.set(
                "Storage",
                "NOTES_PATH",
                os.environ.get("NOTES_PATH", str(Path("~").expanduser())),
            )
            app_config.write()

        self.error_message = event.message
        self.display_state_trigger("error")

    def process_back_button_event(self, event: BackButtonEvent):
        # The display state when button was pressed
        ds = event.display_state
        if ds == "choose":
            # Cannot go further back
            App.get_running_app().stop()
        elif ds == "display":
            set_ds_choose = lambda dt: self.display_state_trigger("choose")
            sch_cb(0, set_ds_choose)
        elif ds == "list":
            set_ds_display = lambda dt: self.display_state_trigger("display")
            sch_cb(0, set_ds_display)
        elif ds == "edit":
            self.registry.push_event(CancelEditEvent())
        elif ds == "add":
            self.registry.push_event(CancelEditEvent())
        else:
            Logger.warning(
                f"Unknown display state encountered when handling back button: {ds}"
            )

    def process_discover_category_event(self, event: DiscoverCategoryEvent):
        event_category = event.category
        if event_category not in self.note_categories:
            Logger.debug(f"NoteDiscoveryEvent: {event_category}")
            self.note_categories.append(event_category)

    def process_event(self, dt):
        if len(self.registry.events) == 0:
            return
        event = self.registry.events.popleft()
        Logger.debug(f"Processing Event: {event}")
        event_type = event.event_type
        func = getattr(self, f"process_{event_type}_event")
        return func(event)

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # Esc Key
            # Back Button Event
            self.registry.push_event(BackButtonEvent(display_state=self.display_state))
            return True
        else:
            return False

    """Kivy"""

    def build(self):

        truthy = {"1", "True"}

        self.registry.app = self
        self.play_state_trigger = trigger_factory(
            self, "play_state", self.__class__.play_state.options
        )
        self.display_state_trigger = trigger_factory(
            self, "display_state", self.__class__.display_state.options
        )
        Window.bind(on_keyboard=self.key_input)
        storage_path = (
            np if (np := self.config.get("Storage", "NOTES_PATH")) != "None" else None
        )
        if storage_path:
            self.registry.storage_path = storage_path

        self.note_service.new_first = (
            True if self.config.get("Behavior", "NEW_FIRST") in truthy else False
        )

        sm = NoteAppScreenManager(self)
        self.screen_manager = sm
        self.play_state = (
            "play" if self.config.get("Behavior", "PLAY_STATE") in truthy else "pause"
        )
        self.note_category = self.config.get("Behavior", "CATEGORY_SELECTED")
        self.base_font_size = self.config.get("Display", "BASE_FONT_SIZE")
        self.registry.query_all()
        Clock.schedule_interval(self.process_event, 0.1)
        self.plugin_manager.init_app(self)
        sm.fbind(
            "on_interact", lambda x: self.plugin_manager.plugin_event("on_interact")
        )
        return sm

    def build_settings(self, settings):
        settings.add_json_panel("MindRef", self.config, data=json.dumps(app_settings))

    def build_config(self, config):
        get_environ = os.environ.get
        # If android we have a special homedir available with NOTES_PATH
        config.setdefaults(
            "Storage",
            {"NOTES_PATH": get_environ("NOTES_PATH", str(Path("~").expanduser()))},
        )
        config.setdefaults(
            "Display", {"BASE_FONT_SIZE": 16, "SCREEN_HEIGHT": 640, "SCREEN_WIDTH": 800}
        )
        config.setdefaults(
            "Behavior",
            {
                "NEW_FIRST": True,
                "PLAY_STATE": False,
                "CATEGORY_SELECTED": "",
                "TRANSITIONS": "Slide",
            },
        )
        config.setdefaults(
            "Plugins", {"SCREEN_SAVER_ENABLE": False, "SCREEN_SAVER_DELAY": 60}
        )

    def on_config_change(self, config, section, key, value):

        truthy = {True, 1, "1", "True"}

        if section == "Storage":
            if key == "NOTES_PATH":
                self.note_service.storage_path = value
                self.display_state_trigger("choose")
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
        elif section == "Behavior":
            if key == "LOG_LEVEL":
                self.log_level = value
            elif key == "NEW_FIRST":
                self.note_service.new_first = True if value in truthy else False
                self.display_state_trigger("choose")
                self.registry.push_event(RefreshNotesEvent(on_complete=None))
            elif key == "PLAY_STATE":
                ...  # No effect here, this is on first load
            elif key == "TRANSITIONS":
                self.screen_transitions = value
        elif section == "Display":
            if key == "BASE_FONT_SIZE":
                self.base_font_size = value
        elif section == "Plugins":
            return False


if __name__ == "__main__":
    MindRefApp().run()
