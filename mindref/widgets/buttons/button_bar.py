from kivy import Logger
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner, SpinnerOption

from domain.events import AddNoteEvent, EditNoteEvent
from utils import import_kv
from widgets.buttons.buttons import ThemedButton

import_kv(__file__)


class ControllerButtonBar(BoxLayout):
    ...


class NoteSpinnerOption(SpinnerOption):
    ...


class NoteActionDropDown(DropDown):
    ...


class NoteActionButton(ThemedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dd = None
        fbind = self.fbind

        fbind("on_release", self.open_dropdown)

    def handle_select(self, instance, value):
        app = App.get_running_app()
        if value == "add":
            app.registry.push_event(AddNoteEvent())
        elif value == "edit":
            app.registry.push_event(
                EditNoteEvent(category=app.note_category, idx=app.note_data["idx"])
            )
        else:
            Logger.warn(f"NoteActionButton: Unknown Event {value}")

    def open_dropdown(self, dt):
        self.dd = NoteActionDropDown()
        self.dd.bind(on_select=self.handle_select)
        self.dd.open(self)
