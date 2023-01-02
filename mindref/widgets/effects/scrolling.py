from math import sin

from kivy.clock import Clock
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout
from .scrolling_c import compute_overscroll
from utils import import_kv, get_app

import_kv(__file__)


class RefreshSymbol(FloatLayout):
    """Spinning Refresh Symbol"""

    rotation = NumericProperty(0)
    event_dt = NumericProperty(0)
    source = StringProperty(None)

    def __init__(self, **kwargs):
        self.source = get_app().atlas_service.uri_for("refresh", atlas_name="icons")
        super(RefreshSymbol, self).__init__(**kwargs)
        self._scheduler = None

    def on_parent(self, *_args):
        if self._scheduler:
            self._scheduler.cancel()
            self._scheduler = None
        if self.parent:
            self._scheduler = Clock.schedule_interval(self.increment_spin, 1 / 60)
            self._scheduler()

    def increment_spin(self, dt):

        self.event_dt = self.event_dt + dt
        rot = (sin(self.event_dt) * 3) - 5
        self.rotation = self.rotation + rot


class RefreshOverscrollEffect(OpacityScrollEffect):
    """
    Reduces opacity when over-scrolling up
    """

    refresh_triggered_ = BooleanProperty(False)
    refresh_triggered = BooleanProperty(False)
    target_height = NumericProperty(0)
    overscroll_refresh_threshold = NumericProperty(0.25)
    overscroll_threshold = NumericProperty(0.10)
    min_opacity = NumericProperty(0.25)
    min_state_time = NumericProperty(0.75)
    parent: ObjectProperty

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_scheduler = None
        self.bind(refresh_triggered_=self.schedule_refresh_check)

    def on_target_widget(self, *_args):
        if self.target_widget:
            self.bind(
                refresh_triggered=self.target_widget.parent.setter("refresh_triggered"),
                refresh_triggered_=self.refresh_unset,
            )
            self.target_widget.bind(height=self.setter("target_height"))
        else:
            self.unbind(
                refresh_triggered=self.target_widget.parent.setter("refresh_triggered"),
                refresh_triggered_=self.refresh_unset,
            )
            self.target_widget.unbind(height=self.setter("target_height"))

    def refresh_unset(self, *_args):
        if not self.refresh_triggered_:
            self.refresh_triggered = False

    def refresh_hold_callback(self, *_args):
        """Check if refresh_triggered_ is still True after delay"""
        if self.refresh_triggered_:
            self.refresh_triggered = True
        return False

    def schedule_refresh_check(self, *_args):
        if self.refresh_scheduler:
            self.refresh_scheduler.cancel()
            self.refresh_scheduler = None
        if self.refresh_triggered_:
            self.refresh_scheduler = Clock.schedule_interval(
                self.refresh_hold_callback, self.min_state_time
            )
            self.refresh_scheduler()

    def on_overscroll(self, *args):
        """
        When we overscroll, we want to mirror the effect of OpacityScrollEffect, but only when over-scrolling up
        (when overscroll is negative).

        Additionally, we want to trigger a refresh but only when the user has held the overscroll for a configurable
        amount of time AND past a configurable threshold for overscroll.
        """

        target_opacity, should_refresh = compute_overscroll(
            self.overscroll,
            self.target_height,
            self.overscroll_threshold,
            self.overscroll_refresh_threshold,
            self.min_opacity,
        )
        self.target_widget.opacity = target_opacity
        self.refresh_triggered_ = should_refresh
        return
