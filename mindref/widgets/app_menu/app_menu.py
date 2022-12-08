from typing import Literal, TYPE_CHECKING

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView

from domain.events import CreateCategoryEvent
from utils import import_kv

import_kv(__file__)

MENU_BUTTON_NAMES = Literal["Settings", "New Category"]

if TYPE_CHECKING:
    from domain.protocols import AppRegistryProtocol


class AppMenu(ModalView):
    btnroot = ObjectProperty()

    def __init__(self, **kwargs):
        super(AppMenu, self).__init__(**kwargs)
        self.register_event_type("on_release")

    def on_release(self, release: MENU_BUTTON_NAMES):
        app: "AppRegistryProtocol" = App.get_running_app()
        match release:
            case "Settings":
                return app.open_settings()
            case "New Category":
                app.registry.push_event(
                    CreateCategoryEvent(action=CreateCategoryEvent.Action.OPEN_FORM)
                )
