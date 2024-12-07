from kivy.logger import Logger
from kivy.uix.dropdown import DropDown

from mindref.lib.utils import import_kv
from mindref.lib.widgets.buttons.buttons import ThemedButton

import_kv(__file__)


class NoteActionDropDown(DropDown): ...


class NoteActionButton(ThemedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dd = None
        fbind = self.fbind
        fbind("on_release", self.open_dropdown)
        self.register_event_type("on_select")

    def on_select(self, value): ...

    def handle_select(self, _, value):
        Logger.info(f"{type(self).__name__}: dispatching 'on_select' : '{value}'")
        self.dispatch("on_select", value)
        return True

    def open_dropdown(self, *_args):
        self.dd = NoteActionDropDown()
        self.dd.bind(on_select=self.handle_select)
        self.dd.open(self)
