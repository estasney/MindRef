from kivy import Logger
from kivy.properties import (
    ObjectProperty,
    BooleanProperty,
    ListProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout

from utils import import_kv

import_kv(__file__)


class PickerDialog(FloatLayout):
    filters = ListProperty()
    dirselect = BooleanProperty()
    on_accept = ObjectProperty()
    on_cancel = ObjectProperty()
    start_folder = StringProperty()
    chooser = ObjectProperty()

    def __init__(self, on_accept, on_cancel, **kwargs):
        super().__init__(**kwargs)
        self.on_accept = on_accept
        self.on_cancel = on_cancel
        self.register_event_type("on_button_event")

    def on_chooser(self, *_args):
        if self.start_folder:
            self.chooser.path = self.start_folder

    def on_button_event(self, event, *args):
        Logger.info(f"{type(self).__name__}: on_button_event - {event} - {args}")
        if event == "accept":
            _, file_path = args
            self.on_accept(file_path[0])
        else:
            self.on_cancel(*args)
        return True


class LoadDialog(PickerDialog):
    chooser = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SaveDialog(PickerDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
