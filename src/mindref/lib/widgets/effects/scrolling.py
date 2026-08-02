from enum import StrEnum
from math import sin

from kivy.animation import Animation
from kivy.clock import Clock, ClockEvent
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout

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


class RefreshState(StrEnum):
    """
    Enum for the refresh state
    """

    hidden = "hidden"
    visible = "visible"
    active = "active"


class RefreshSymbol(FloatLayout):
    """Spinning Refresh Symbol"""

    rotation = NumericProperty(0)
    event_dt = NumericProperty(0)
    opacity = NumericProperty(0)
    source = StringProperty(None, allownone=True)
    animate = BooleanProperty(False)

    _scheduler: ClockEvent | None

    def __init__(self, **kwargs: object):
        self.source = get_app().atlas_service.uri_for("refresh", atlas_name="icons")
        super().__init__(**kwargs)
        self._scheduler = None

    def on_animate(self, _instance: object, value: bool) -> None:
        if value:
            self._scheduler = Clock.schedule_interval(self.increment_spin, 1 / 60)
            self._scheduler()
            return
        if self._scheduler is not None:
            self._scheduler.cancel()
            self._scheduler = None
        Animation(opacity=0, d=0.2).start(self)

    def increment_spin(self, dt):
        self.event_dt = self.event_dt + dt
        rot = (sin(self.event_dt) * 4) + 5
        self.rotation = self.rotation + rot

    def collide_point(self, x, y):
        return False
