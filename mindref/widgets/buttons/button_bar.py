from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown

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
        self.register_event_type("on_select")

    def on_select(self, value):
        ...

    def handle_select(self, _, value):

        Logger.info(f"{type(self).__name__}: Pushing Note Event {value}")
        self.dispatch("on_select", value)
        return True

    def open_dropdown(self, *_args):
        self.dd = NoteActionDropDown()
        self.dd.bind(on_select=self.handle_select)
        self.dd.open(self)
