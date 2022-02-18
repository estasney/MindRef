import os
from functools import partial

from dotenv import load_dotenv
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (DictProperty, ListProperty, NumericProperty, ObjectProperty, OptionProperty,
                             StringProperty)
from kivy.uix.screenmanager import NoTransition, SlideTransition
from sqlalchemy import desc, select

from custom.screens import NoteAppScreenManager
from db import Note, create_session


class NoteIndex:
    """
    Handles indexing notes so that we can always call `next` or `previous`

    As with `range`, `end` is not inclusive
    """

    def __init__(self, size: int, current=0):
        self.size = size
        self.start = 0
        self.end = max([0, (size - 1)])
        self.current = current

    def next(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == self.end:
            self.current = 0
            return self.current
        else:
            self.current += 1
            return self.current

    def previous(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == 0:
            self.current = self.end
            return self.current
        else:
            self.current -= 1
            return self.current


class NoteAFly(App):
    """
    Attributes
    ----------
    db_session
        session used for database
    note_idx
        Uses itertools `cycle` so that calling `next` will yield the next valid index
    notes_data_categorical
        All notes as dict() that have a Category == `self.note_category`
    note_categories: ListProperty
        List of str of all note categories
    note_data: DictProperty
        Data regarding the currently displayed note
    display_state: OptionProperty
        One of [Display, Choose]
        Choose:: Display all known categories
        Display:: Iterate through notes matching `self.note_category`
    screen_manager: ObjectProperty
        Holds the reference to ScreenManager
    colors: DictProperty
        Color scheme

    """

    APP_NAME = 'NoteAFly'

    db_session = None

    note_idx = None
    notes_data_categorical = ListProperty()
    note_categories = ListProperty()
    note_category = StringProperty('')
    note_data = DictProperty(rebind=True)

    next_note_scheduler = ObjectProperty()

    display_state = OptionProperty("choose", options=["choose", "display", "list"])
    play_state = OptionProperty("play", options=["play", "pause"])
    paginate_interval = NumericProperty(15)

    screen_manager = ObjectProperty()

    colors = DictProperty({
        "Light":   (0.3843137254901961, 0.4470588235294118, 0.4823529411764706),
        "Primary": (0.21568627450980393, 0.2784313725490195, 0.30980392156862746),
        "Dark":    (0.06274509803921569, 0.1254901960784313, 0.15294117647058825),
        "Accent1": (0.8588235294117648, 0.227450980392157, 0.20392156862745092),
        "Accent2": (0.02352941176470591, 0.8392156862745098, 0.6274509803921572)
        })

    def _setup_data(self):
        """Initial load of data"""
        self.db_session = create_session()

        category_query = select(Note.category.label("category")).distinct().order_by(Note.category)

        self.note_categories = [row.category.name for row in self.db_session.execute(category_query).all()]

    def on_display_state(self, instance, new):
        if new != 'list':
            return
        self.note_idx = None
        if self.next_note_scheduler:
            self.next_note_scheduler.cancel()

    def select_index(self, value):
        self.note_data = self.notes_data_categorical[value]
        self.note_idx = NoteIndex(len(self.notes_data_categorical), current=value)
        self.play_state = 'pause'
        self.display_state = 'display'

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
        direction = kwargs.get('direction', 1)
        is_initial = kwargs.get('initial', False)
        """Update `self.note_data` from `self.notes_data`"""
        if is_initial:
            self.note_data = self.notes_data_categorical[0]
        else:
            if direction > 0:
                note = self.notes_data_categorical[self.note_idx.next()]
            else:
                note = self.notes_data_categorical[self.note_idx.previous()]
            self.note_data = note

    def on_play_state(self, instance, value):
        if value == "pause":
            self.next_note_scheduler.cancel()
        else:
            self.next_note_scheduler()

    def on_note_category(self, instance, value):
        if not value:
            self.notes_data_categorical = []
            self.note_idx = None
            if self.next_note_scheduler:
                self.next_note_scheduler.cancel()
            self.display_state = "choose"
        else:
            category_stmt = select(Note).filter(Note.category == value).order_by(desc(Note.id))
            self.notes_data_categorical = [{"idx": i, **row.Note.to_dict()}
                                           for i, row in enumerate(self.db_session.execute(category_stmt).all())]
            self.note_idx = NoteIndex(len(self.notes_data_categorical))
            if not self.next_note_scheduler:
                self.next_note_scheduler = Clock.schedule_interval(self.paginate_note, self.paginate_interval)
                if self.play_state == 'pause':
                    self.next_note_scheduler.cancel()
            else:
                if self.play_state == 'play':
                    self.next_note_scheduler()
            self.paginate_note(initial=True)
            self.display_state = "display"

    def on_note_data(self, *args, **kwargs):
        self.screen_manager.handle_notes(self)

    def build(self):
        self._setup_data()
        sm = NoteAppScreenManager(self, transition=NoTransition() if os.environ.get("NO_TRANSITION", False) else SlideTransition())
        self.screen_manager = sm
        return sm


if __name__ == '__main__':
    load_dotenv()
    NoteAFly().run()
