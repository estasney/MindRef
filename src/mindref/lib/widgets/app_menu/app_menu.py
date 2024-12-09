from typing import Literal

from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout

from mindref.lib.domain.events import CreateCategoryEvent
from mindref.lib.utils import get_app, import_kv, sch_cb, schedulable

import_kv(__file__)

MENU_BUTTON_NAMES = Literal["Settings", "New Category"]


class AppMenu(AnchorLayout):
    btnroot = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_release")
        self.register_event_type("on_dismiss")

    def on_dismiss(self, *_args): ...

    def on_release(self, release: MENU_BUTTON_NAMES):
        app = get_app()
        dismiss_self = schedulable(self.dispatch, "on_dismiss")
        match release:
            case "Settings":
                sch_cb(dismiss_self, app.open_settings, timeout=0.1)
            case "New Category":
                event = CreateCategoryEvent(action=CreateCategoryEvent.Action.OPEN_FORM)
                push_event = schedulable(app.registry.push_event, event)
                sch_cb(dismiss_self, push_event, timeout=0.1)
            case "Exit":
                sch_cb(dismiss_self, app.stop, timeout=0.1)
