from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from domain.events import CreateCategoryEvent
from utils import import_kv, get_app, attrsetter, sch_cb, caller
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
        self.register_event_type("on_save")
        self.register_event_type("on_cancel")

    def clear_inputs(self, *_args):
        self.category_name_input.text = ""
        self.image_path_input.text = ""

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
