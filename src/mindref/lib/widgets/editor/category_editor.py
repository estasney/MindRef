from collections.abc import Callable
from typing import Literal

from kivy import Logger
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.domain.events import CreateCategoryEvent, FilePickerEvent
from mindref.lib.utils import get_app, import_kv, sch_cb, schedulable
from mindref.lib.widgets.forms.text_field import TextField

import_kv(__file__)


class CategoryEditor(BoxLayout):
    category_name_input: TextField = ObjectProperty()
    image_path_input: TextField = ObjectProperty()
    validator: Callable[[tuple[str, str]], str | None] = ObjectProperty()
    allow_submit = BooleanProperty(False)

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        kwargs
        """
        super().__init__(**kwargs)

    def validate(self, _instance, touched: bool, field: str):
        """
        Parameters
        ----------
        _instance
        touched : bool
            True if the input is touched
        field : str
            The field that was touched

        If widget is touched and has text, send to validator. The inputs are bound to this method in the kv file
        """

        w_field = self.category_name_input if field == "name" else self.image_path_input
        if touched and (field_txt := w_field.text):
            msg: str | None = self.validator(field, field_txt)
            Logger.info(f"{type(self).__name__}: validate - {field}[msg={msg}]")
            if msg:
                w_field.error_message = msg
            else:
                w_field.error_message = ""

    def clear_inputs(self, *_args):
        self.category_name_input.clear()
        self.image_path_input.clear()

    def button_event(self, event: Literal["save", "cancel", "browse"]):
        """

        Parameters
        ----------
        event : Literal["save", "cancel", "browse"]
            The event that was triggered
        """
        app = get_app()

        match event:
            case "save":
                cat_event = CreateCategoryEvent(
                    action=CreateCategoryEvent.Action.CLOSE_ACCEPT,
                    category=self.category_name_input.text,
                    img_path=self.image_path_input.text,
                )
                push_cat_event = schedulable(app.registry.push_event, cat_event)
                sch_cb(push_cat_event, self.clear_inputs, timeout=0.1)
            case "cancel":
                cat_event = CreateCategoryEvent(
                    action=CreateCategoryEvent.Action.CLOSE_FORM
                )
                push_cat_event = schedulable(app.registry.push_event, cat_event)
                sch_cb(push_cat_event, self.clear_inputs, timeout=0.1)
            case "browse":
                set_result = lambda x: setattr(
                    self.image_path_input.w_text_input, "text", x
                )
                browse_event = FilePickerEvent(
                    on_complete=set_result,
                    action=FilePickerEvent.Action.OPEN_FILE,
                    ext_filter=["*.png", "*.jpg", "*.jpeg"],
                )
                push_browse_event = schedulable(app.registry.push_event, browse_event)
                sch_cb(push_browse_event)

    def on_cancel(self, *_args):
        app = get_app()
        event = CreateCategoryEvent(action=CreateCategoryEvent.Action.CLOSE_FORM)
        push_event = schedulable(app.registry.push_event, event)
        sch_cb(push_event, self.clear_inputs, timeout=0.1)

    def on_save(self, *_args):
        app = get_app()
        event = CreateCategoryEvent(
            action=CreateCategoryEvent.Action.CLOSE_ACCEPT,
            category=self.category_name_input.text,
            img_path=self.image_path_input.text,
        )
        push_event = schedulable(app.registry.push_event, event)
        sch_cb(push_event, self.clear_inputs, timeout=0.1)
