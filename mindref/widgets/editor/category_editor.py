from typing import Literal

from kivy.properties import StringProperty, ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from domain.events import CreateCategoryEvent, FilePickerEvent
from utils import import_kv, get_app, attrsetter, sch_cb, caller, def_cb
from widgets.buttons.buttons import TexturedButton

import_kv(__file__)


class LabeledInput(BoxLayout):
    label_text = StringProperty()
    value = StringProperty()


class OpenFileDialogButton(TexturedButton):
    ...


class CategoryEditor(BoxLayout):
    category_name_input: TextInput = ObjectProperty()
    image_path_input: TextInput = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clear_inputs(self, *_args):
        self.category_name_input.text = ""
        self.image_path_input.text = ""

    def button_event(self, event: Literal["save", "cancel", "browse"]):
        app = get_app()
        push_event = partial(caller, app.registry, "push_event")

        match event:
            case "save":
                event = CreateCategoryEvent(
                    action=CreateCategoryEvent.Action.CLOSE_ACCEPT,
                    category=self.category_name_input.text,
                    img_path=self.image_path_input.text,
                )
                push_event = push_event(event)
                sch_cb(push_event, self.clear_inputs, timeout=0.1)
            case "cancel":
                event = CreateCategoryEvent(
                    action=CreateCategoryEvent.Action.CLOSE_FORM
                )
                push_event(event)
                sch_cb(push_event, self.clear_inputs, timeout=0.1)
            case "browse":
                set_result = lambda x: setattr(self.image_path_input, "text", x)
                event = FilePickerEvent(
                    on_complete=set_result,
                    action=FilePickerEvent.Action.OPEN_FILE,
                    ext_filter=["*.png", "*.jpg", "*.jpeg"],
                )
                push_event = push_event(event)
                sch_cb(push_event)

    def on_cancel(self, *_args):
        app = get_app()
        event = CreateCategoryEvent(action=CreateCategoryEvent.Action.CLOSE_FORM)
        push_event = caller(app.registry, "push_event", event)
        sch_cb(push_event, self.clear_inputs, timeout=0.1)

    def on_save(self, *_args):
        app = get_app()
        event = CreateCategoryEvent(
            action=CreateCategoryEvent.Action.CLOSE_ACCEPT,
            category=self.category_name_input.text,
            img_path=self.image_path_input.text,
        )
        push_event = caller(app.registry, "push_event", event)
        sch_cb(push_event, self.clear_inputs, timeout=0.1)
