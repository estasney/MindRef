import logging
import os
from functools import partial
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import (
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.screenmanager import NoTransition, SlideTransition

from services.atlas.atlas import AtlasService
from services.backend.fileStorage.fileBackend import FileSystemBackend
from widgets.screens import NoteAppScreenManager


class NoteAFly(App):
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

    APP_NAME = "NoteAFly"
    atlas_service = AtlasService(storage_path=Path("./static").resolve())
    note_service = FileSystemBackend(
        new_first=True,
        storage_path=Path(os.environ.get("NOTES_PATH")).expanduser().resolve(),
    )
    note_categories = ListProperty(note_service.categories)
    note_category = StringProperty("")
    note_data = DictProperty(rebind=True)
    note_category_meta = ListProperty()
    next_note_scheduler = ObjectProperty()

    display_state = OptionProperty("choose", options=["choose", "display", "list"])
    play_state = OptionProperty("play", options=["play", "pause"])
    paginate_interval = NumericProperty(15)
    log_level = NumericProperty(logging.ERROR)

    screen_manager = ObjectProperty()
    fonts = DictProperty({"mono": "RobotoMono", "default": "Roboto"})
    colors = DictProperty(
        {
            "White": (1, 1, 1),
            "Codespan": (0, 0, 0, 0.15),
            "Gray": (0.7803921568627451, 0.7803921568627451, 0.7803921568627451, 1),
            "Light": (0.3843137254901961, 0.4470588235294118, 0.4823529411764706, 1),
            "Primary": (
                0.21568627450980393,
                0.2784313725490195,
                0.30980392156862746,
                1,
            ),
            "Dark": (0.06274509803921569, 0.1254901960784313, 0.15294117647058825, 1),
            "Accent1": (0.8588235294117648, 0.227450980392157, 0.20392156862745092, 1),
            "Accent2": (0.02352941176470591, 0.8392156862745098, 0.6274509803921572, 1),
            "LightBlue": (
                0.4470588235294118,
                0.6235294117647059,
                0.8117647058823529,
                1.0,
            ),
        }
    )

    def on_display_state(self, instance, new):
        if new != "list":
            return
        if self.next_note_scheduler:
            self.next_note_scheduler.cancel()

    def select_index(self, value):
        self.note_service.set_index(value)
        self.note_data = self.note_service.current_note().to_dict()
        self.play_state = "pause"
        self.display_state = "display"

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
        if not value:
            self.note_category_meta = []
            if self.next_note_scheduler:
                self.next_note_scheduler.cancel()
            self.display_state = "choose"
        else:
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

    def on_note_data(self, *args, **kwargs):
        self.screen_manager.handle_notes(self)

    def build(self):
        sm = NoteAppScreenManager(
            self,
            transition=NoTransition()
            if os.environ.get("NO_TRANSITION", False)
            else SlideTransition(),
        )
        self.screen_manager = sm
        self.play_state = os.environ.get("PLAY_STATE", "play")
        self.note_category = os.environ.get("CATEGORY_SELECTED", "")
        self.log_level = int(os.environ.get("LOG_LEVEL", logging.INFO))

        return sm


if __name__ == "__main__":
    NoteAFly().run()
