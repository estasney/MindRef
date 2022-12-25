from functools import partial
from typing import Literal, TYPE_CHECKING

from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView

from domain.events import CreateCategoryEvent
from utils import import_kv, get_app, sch_cb, caller

import_kv(__file__)

MENU_BUTTON_NAMES = Literal["Settings", "New Category"]

if TYPE_CHECKING:
    pass


class AppMenu(ModalView):
    btnroot = ObjectProperty()

    def __init__(self, **kwargs):
        super(AppMenu, self).__init__(**kwargs)
        self.register_event_type("on_release")

    def on_release(self, release: MENU_BUTTON_NAMES):
        app = get_app()
        dismiss_self = caller(self, "dispatch", "on_dismiss")
        match release:
            case "Settings":
                sch_cb(dismiss_self, app.open_settings, timeout=0.1)
            case "New Category":
                event = CreateCategoryEvent(action=CreateCategoryEvent.Action.OPEN_FORM)
                push_event = caller(app.registry, "push_event", event)
                sch_cb(dismiss_self, push_event, timeout=0.1)
