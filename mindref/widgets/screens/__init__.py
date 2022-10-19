from typing import Optional

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from widgets.behavior.interact_behavior import InteractBehavior
from widgets.behavior.refresh_behavior import RefreshBehavior
from widgets.effects.scrolling import RefreshSymbol


class InteractScreen(InteractBehavior, Screen):
    ...


class RefreshableScreen(InteractBehavior, RefreshBehavior, Screen):
    refresh_icon: Optional[RefreshSymbol]

    """
    Mixin class that adds custom event 'on_refresh'
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_refresh_symbol_trigger = Clock.create_trigger(self._add_refresh_symbol)
        self.remove_refresh_symbol_trigger = Clock.create_trigger(
            self._clear_refresh_symbol
        )
        self.register_event_type("on_refresh")
        self.refresh_icon = None

    def _add_refresh_symbol(self, dt):
        """
        Add a refresh Icon, if we don't have one already
        """
        if not self.refresh_icon:
            self.refresh_icon = RefreshSymbol(
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            self.add_widget(self.refresh_icon)

    def _clear_refresh_symbol(self, *args, **kwargs):
        if self.refresh_icon:
            self.remove_widget(self.refresh_icon)
            del self.refresh_icon
            self.refresh_icon = None
