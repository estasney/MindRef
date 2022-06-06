from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout

from utils import import_kv

import_kv(__file__)


class RefreshSymbol(FloatLayout):
    """Spinning Refresh Symbol"""

    rotation = NumericProperty(0)
    source = StringProperty(None)

    def __init__(self, **kwargs):
        self.source = App.get_running_app().atlas_service.uri_for(
            "refresh", atlas_name="icons"
        )
        super(RefreshSymbol, self).__init__(**kwargs)
        self._scheduler = None

    def on_parent(self, instance, value):
        if self._scheduler:
            self._scheduler.cancel()
            self._scheduler = None
        if self.parent:
            self._scheduler = Clock.schedule_interval(self.increment_spin, 1 / 60)
            self._scheduler()

    def increment_spin(self, dt):
        self.rotation -= 5


class RefreshOverscrollEffect(OpacityScrollEffect):
    """
    Reduces opacity when over-scrolling up
    """

    refresh_triggered_ = BooleanProperty(False)
    refresh_triggered = BooleanProperty(False)
    parent: ObjectProperty

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_scheduler = None
        self.bind(refresh_triggered_=self.schedule_refresh_check)

    def on_target_widget(self, instance, value):
        self.bind(
            refresh_triggered=self.target_widget.parent.setter("refresh_triggered")
        )
        self.bind(refresh_triggered_=self.refresh_unset)

    def refresh_unset(self, instance, value):
        if not self.refresh_triggered_:
            Logger.debug("Refresh Triggered -> False")
            self.refresh_triggered = False

    def refresh_hold_callback(self, dt):
        """Check if refresh_triggered_ is still True after delay"""
        if self.refresh_triggered_:
            self.refresh_triggered = True
        return False

    def schedule_refresh_check(self, instance, value):
        if self.refresh_scheduler:
            self.refresh_scheduler.cancel()
            self.refresh_scheduler = None
        if self.refresh_triggered_:
            self.refresh_scheduler = Clock.schedule_interval(
                self.refresh_hold_callback, 0.05
            )
            self.refresh_scheduler()

    def on_overscroll(self, *args):
        self.trigger_velocity_update()
        if self.target_widget and self.target_widget.height != 0:
            if self.overscroll > 50:
                self.refresh_triggered_ = False
                self.target_widget.opacity = 1
            elif -5 <= self.overscroll <= 5:
                self.refresh_triggered_ = False
                self.target_widget.opacity = 1
            else:
                ratio = abs(self.overscroll / self.target_widget.height)
                alpha = max(0.1, 1 - ratio - 0.3)
                # noinspection PyTypeChecker
                self.target_widget.opacity = min(1, alpha)
                if ratio >= 0.25:
                    self.refresh_triggered_ = True
                else:
                    self.refresh_triggered_ = False
            # self.trigger_velocity_update()
