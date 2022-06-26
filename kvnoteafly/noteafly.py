import logging
import os
from functools import partial
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
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
    CancelEditEvent,
    EditNoteEvent,
    NoteFetchedEvent,
    NotesQueryEvent,
    RefreshNotesEvent,
    SaveNoteEvent,
)
from domain.settings import (
    SETTINGS_BEHAVIOR_PATH,
    SETTINGS_DISPLAY_PATH,
    SETTINGS_STORAGE_PATH,
)
from service.registry import Registry
from utils import sch_cb
from widgets.screens import NoteAppScreenManager


class NoteAFly(App):
    APP_NAME = "NoteAFly"
    atlas_service = AtlasService(storage_path=Path("./static").resolve())
    note_service = FileSystemNoteRepository(new_first=True)
    editor_service = FileSystemEditor()

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
        "choose", options=["choose", "display", "list", "edit", "add"]
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

        if new in {"edit", "add"}:
            self.play_state = "pause"
        if new == "edit":
            self.editor_note = self.editor_service.edit_current_note(self)

        elif new == "add":
            self.editor_note = self.editor_service.new_note(
                category=self.note_category, idx=self.note_service.index_size()
            )
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

    def process_cancel_edit_event(self, event: CancelEditEvent):
        update_display_state = lambda x: setattr(self, "display_state", "display")
        clear_edit_note = lambda x: setattr(self, "editor_note", None)
        sch_cb(0, update_display_state, clear_edit_note)

    def process_edit_note_event(self, event: EditNoteEvent):
        data_note = self.registry.edit_note(category=event.category, idx=event.idx)
        update_edit_note = lambda x: setattr(self, "editor_note", data_note)
        update_display_state = lambda x: setattr(self, "display_state", "edit")
        sch_cb(0, update_edit_note, update_display_state)

    def process_add_note_event(self, event: AddNoteEvent):
        data_note = self.registry.new_note(category=self.note_category, idx=None)
        update_edit_note = lambda x: setattr(self, "editor_note", data_note)
        update_display_mode = lambda x: setattr(self, "display_state", "add")
        sch_cb(0, update_edit_note, update_display_mode)

    def process_save_note_event(self, event: SaveNoteEvent):
        note_is_new = self.display_state == "add"
        data_note = self.editor_note
        data_note.edit_text = event.text
        if note_is_new:
            data_note.edit_title = event.title
        update_edit_note = lambda x: setattr(self, "editor_note", None)
        update_display_state = lambda x: setattr(self, "display_state", "display")
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

    def process_notes_query_event(self, event: NotesQueryEvent):
        def append_category_factory(category):
            def append_category(dt, c):
                current = [c for c in self.note_categories]
                current.append(c)
                self.note_categories = current

            func = partial(append_category, c=category)
            return func

        steps = [
            append_category_factory(c) for c in [d["category"] for d in event.result]
        ]

        if event.on_complete is not None:
            steps.append(event.on_complete)

        sch_cb(0, *steps)

    def process_event(self, dt):
        if len(self.registry.events) == 0:
            return
        event = self.registry.events.popleft()
        Logger.debug(f"Processing Event: {event}")
        event_type = event.event_type
        func = getattr(self, f"process_{event_type}_event")
        return func(event)

    def build(self):
        self.registry.app = self
        storage_path = (
            np if (np := self.config.get("Storage", "NOTES_PATH")) != "None" else None
        )
        if storage_path:
            self.registry.storage_path = storage_path

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
        self.registry.query_all()
        Clock.schedule_interval(self.process_event, 0.1)
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
