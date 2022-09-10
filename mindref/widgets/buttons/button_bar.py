from kivy.app import App
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown

from domain.events import (
    AddNoteEvent,
    BackButtonEvent,
    EditNoteEvent,
    ListViewButtonEvent,
)
from utils import import_kv
from widgets.buttons.buttons import TexturedButton

import_kv(__file__)


class ControllerButtonBar(BoxLayout):
    ...


class NoteActionDropDown(DropDown):
    ...


class NoteActionButton(TexturedButton):
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
        elif value == "list":
            app.registry.push_event(ListViewButtonEvent())
        elif value == "back":
            app.registry.push_event(BackButtonEvent(current_display_state="display"))
        else:
            Logger.warn(f"NoteActionButton: Unknown Event {value}")

    def open_dropdown(self, dt):
        self.dd = NoteActionDropDown()
        self.dd.bind(on_select=self.handle_select)
        self.dd.open(self)
