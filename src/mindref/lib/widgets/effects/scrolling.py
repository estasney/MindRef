from enum import Enum
from math import sin

from kivy.logger import Logger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout

from mindref.lib.ext import compute_overscroll
from mindref.lib.utils import get_app

Builder.load_string("""
<RefreshSymbol>:
    size_hint_y: None
    size_hint_x: None
    width: dp(80)
    height: dp(80)
    pos_hint: {"center_x": 0.5, "center_y": 0.9}

    canvas.before:
        PushMatrix
        Rotate:
            angle: self.rotation
            origin: self.center
    canvas:
        Color:
            rgba: (*app.colors['White'], self.opacity)
        Rectangle:
            size: root.size
            pos: self.pos
            source: self.source
    canvas.after:
        PopMatrix
""")


class RefreshState(str, Enum):
    """
    Enum for the refresh state
    """

    HIDDEN = "hidden"
    VISIBLE = "visible"
    ACTIVE = "active"

    def __str__(self) -> str:
        return str.__str__(self)


class RefreshSymbol(FloatLayout):
    """Spinning Refresh Symbol"""

    rotation = NumericProperty(0)
    event_dt = NumericProperty(0)
    opacity = NumericProperty(0)
    source = StringProperty(None, allownone=True)
    animate = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.source = get_app().atlas_service.uri_for("refresh", atlas_name="icons")
        super().__init__(**kwargs)
        self._scheduler = None

    def on_animate(self, _, value):
        if value:
            self._scheduler = Clock.schedule_interval(self.increment_spin, 1 / 60)
            self._scheduler()
        else:
            self._scheduler.cancel()
            self._scheduler = None
            Animation(opacity=0, d=0.2).start(self)

    def increment_spin(self, dt):
        self.event_dt = self.event_dt + dt
        rot = (sin(self.event_dt) * 4) + 5
        self.rotation = self.rotation + rot

    def collide_point(self, x, y):
        return False


class RefreshOverscrollEffect(OpacityScrollEffect):
    """
    Reduces opacity when over-scrolling up
    """

    min_opacity = NumericProperty(0.25)
    target_height = NumericProperty(0)
    refresh_threshold = NumericProperty(
        0.25
    )  # how far to pull (0..1) to trigger refresh
    refresh_threshold_met = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_scheduler = None

    def on_refresh_threshold_met(self, *args):
        Logger.info(f"Refresh threshold met: {self.refresh_threshold_met}")

    def on_overscroll(self, *args):
        """
        When we overscroll, we want to mirror the effect of OpacityScrollEffect, but only when over-scrolling up
        (when overscroll is negative).

        Additionally, we want to trigger a refresh but only when the user has held the overscroll for a configurable
        amount of time AND past a configurable threshold for overscroll.
        """
        if self.overscroll >= 0:
            return

        normalized_overscroll = compute_overscroll(
            self.overscroll, Window.height, self.refresh_threshold
        )
        self.refresh_threshold_met = normalized_overscroll == 1
