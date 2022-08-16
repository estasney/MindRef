from kivy.uix.boxlayout import BoxLayout
from domain.events import AddNoteEvent, BackButtonEvent, EditNoteEvent
from utils import import_kv

import_kv(__file__)


class ControllerButtonBar(BoxLayout):
    ...


class NoteActionButtonBar(BoxLayout):
    def push_add_event(self, app):
        app.registry.push_event(AddNoteEvent())

    def push_edit_event(self, app, category: str, idx: int):
        app.registry.push_event(EditNoteEvent(category=category, idx=idx))
