from typing import TYPE_CHECKING

from kivy import Logger
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.scrollview import ScrollView

from mindref.lib.domain.events import RefreshNotesEvent
from mindref.lib.utils import def_cb, get_app, import_kv
from mindref.lib.widgets.screens.interactive import RefreshableScreen

if TYPE_CHECKING:
    from mindref.lib.widgets.buttons.category import NoteCategoryButton

import_kv(__file__)


class NoteCategoryChooserScreen(RefreshableScreen):
    chooser = ObjectProperty()
    refresh_triggered = BooleanProperty(False)
    refresh_dispatched = BooleanProperty(False)

    """
    Attributes
    ----------
    chooser
    refresh_triggered
        Set to true when a refresh is triggered with the overscroll effect
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_refresh_trigger = Clock.create_trigger(self._dispatch_refresh)

    def on_refresh(self, state: bool):
        Logger.debug(f"{type(self).__name__} : on_refresh {state}")
        if state:
            self.add_refresh_symbol_trigger()
        else:
            self.remove_refresh_symbol_trigger()
        return True

    def category_selected(self, category_btn: "NoteCategoryButton"):
        self.manager.category_selected(category_btn)

    def _dispatch_refresh(self, *_args):
        if not self.refresh_dispatched:
            self.refresh_dispatched = True
            Logger.info(f"{type(self).__name__} : Dispatching Refresh Event")
            app = get_app()
            cb = def_cb(
                self.remove_refresh_symbol_trigger,
                lambda _dt: setattr(self, "refresh_dispatched", False),
            )
            app.registry.push_event(RefreshNotesEvent(on_complete=cb))

    def on_refresh_triggered(self, *_args):
        if self.refresh_triggered:
            self.add_refresh_symbol_trigger()
            self.dispatch_refresh_trigger()


class CategoryScreenScrollWrapper(ScrollView):
    """Screen With Buttons for Categories"""

    screen = ObjectProperty()
    chooser = ObjectProperty()
    refresh_triggered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_chooser(self, *_args):
        self.chooser.bind(minimum_height=self.chooser.setter("height"))

    def on_screen(self, *_args):
        self.bind(refresh_triggered=self.screen.setter("refresh_triggered"))

    def category_selected(self, instance: "NoteCategoryButton"):
        self.screen.category_selected(instance)
