import os
from functools import partial
from pathlib import Path

from dotenv import load_dotenv
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    )
from kivy.uix.screenmanager import NoTransition, SlideTransition
from sqlalchemy import desc, select

from custom.screens import NoteAppScreenManager
from db import Note, create_session
from services.backend import NoteIndex
from services.backend.fileBackend import FileSystemBackend

load_dotenv()


class NoteAFly(App):
    """
    Attributes
    ----------
    APP_NAME: str
    note_service: BackendProtocol
    note_categories: ListProperty
        All known note categories
    note_category: StringProperty
        The active Category. If no active category, value is empty string
    note_data: DictProperty
        The active Note belonging to active Category
    next_note_scheduler: ObjectProperty
    display_state: OptionProperty
        One of [Display, Choose]
        Choose:: Display all known categories
        Display:: Iterate through notes matching `self.note_category`
    play:state: OptionProperty
        One of [play, pause]
        play:: schedule pagination through notes
        pause:: stop pagination through notes
    screen_manager: ObjectProperty
        Holds the reference to ScreenManager
    colors: DictProperty
        Color scheme
    """

    APP_NAME = "NoteAFly"
    note_service = FileSystemBackend(storage_path=Path(os.environ.get("NOTES_PATH")).expanduser().resolve())
    note_categories = ListProperty(note_service.categories)
    note_category = StringProperty("")
    note_data = DictProperty(rebind=True)
    notes_data_categorical = ListProperty()
    next_note_scheduler = ObjectProperty()

    display_state = OptionProperty("choose", options=["choose", "display", "list"])
    play_state = OptionProperty("play", options=["play", "pause"])
    paginate_interval = NumericProperty(15)

    screen_manager = ObjectProperty()

    colors = DictProperty(
            {
                "Light":   (0.3843137254901961, 0.4470588235294118, 0.4823529411764706),
                "Primary": (0.21568627450980393, 0.2784313725490195, 0.30980392156862746),
                "Dark":    (0.06274509803921569, 0.1254901960784313, 0.15294117647058825),
                "Accent1": (0.8588235294117648, 0.227450980392157, 0.20392156862745092),
                "Accent2": (0.02352941176470591, 0.8392156862745098, 0.6274509803921572),
                }
            )

    def on_display_state(self, instance, new):
        if new != "list":
            return
        if self.next_note_scheduler:
            self.next_note_scheduler.cancel()

    def select_index(self, value):
        self.note_data = self.note_service.current_note()
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

    def on_play_state(self, instance, value):
        if value == "pause":
            self.next_note_scheduler.cancel()
        else:
            self.next_note_scheduler()

    def on_note_category(self, instance, value: str):
        """
        Category button pressed
        """
        self.note_service.current_category = value
        if not value:
            self.notes_data_categorical = []
            if self.next_note_scheduler:
                self.next_note_scheduler.cancel()
            self.display_state = "choose"
        else:

            self.notes_data_categorical = self.note_service.notes[value]
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

        return sm


if __name__ == "__main__":
    NoteAFly().run()
