from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv
from widgets.buttons.buttons import TexturedButton

import_kv(__file__)


class LabeledInput(BoxLayout):
    label_text = StringProperty()
    value = StringProperty()


class OpenFileDialogButton(TexturedButton):
    ...


class CategoryEditor(BoxLayout):
    category_name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_save")
        self.register_event_type("on_cancel")

    def on_cancel(self, *_args):
        ...

    def on_save(self, *_args):
        ...
