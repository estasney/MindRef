from enum import Enum
from typing import Literal

from kivy import Logger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    partial,
    DictProperty,
)
from kivy.uix.floatlayout import FloatLayout

from mindref.lib.widgets.behavior import CustomBehavior
from mindref.lib.widgets.buttons.buttons import ThemedIconButton


class OpenState(str, Enum):
    open = "open"
    opening = "opening"
    closed = "closed"
    closing = "closing"

    def __str__(self) -> str:
        return str.__str__(self)


TOpenState = Literal["open", "opening", "closed", "closing"]


Builder.load_string(
    """
<NavDrawer>:
    pos_hint: {"left": 0}
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: app.colors['Dark']
        Rectangle:
            size: self.size
            pos: self.pos
"""
)


class NavDrawer(FloatLayout, CustomBehavior):
    size_hint_x_closed = NumericProperty(0)
    size_hint_x_open = NumericProperty(0)
    size_hint_x = NumericProperty(0, allownone=False)
    animation_open_duration = NumericProperty(0.2)
    animation_close_duration = NumericProperty(0.2)
    open_state = OptionProperty(
        OpenState.closed, options=list(OpenState.__members__.values())
    )
    _anim: Animation | None = ObjectProperty(allownone=True)
    _menu_button: ThemedIconButton | None = ObjectProperty(allownone=True)
    _menu_button_pos_hint_closed = DictProperty({"center_x": 0.5, "top": 1})

    __custom_events__ = frozenset({"on_open", "on_close", "on_opening", "on_closing"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._bind_button, 0)

    def _bind_button(self, _dt):
        btn = ThemedIconButton(
            icon_code="\ue5d2",
            size_hint=(None, None),
            pos_hint=self._menu_button_pos_hint_closed,
        )
        btn.bind(height=btn.setter("width"))
        btn.bind(on_release=self.toggle)
        self.add_widget(btn)
        self._menu_button = btn

    def on_size_hint_x_closed(self, _instance, _value):
        self.size_hint_x = _value

    def on_open_state(self, _instance, _value: TOpenState | OpenState):
        match _value:
            case OpenState.open:
                self.dispatch("on_open", _instance, _value)
            case OpenState.closed:
                self.dispatch("on_close", _instance, _value)
            case OpenState.opening:
                self.dispatch("on_opening", _instance, _value)
            case OpenState.closing:
                self.dispatch("on_closing", _instance, _value)
            case _:
                msg = f"Invalid state: {_value}"
                raise ValueError(msg)

    def on_open(self, _instance, _value):
        Logger.info("Drawer opened")
        self._anim = None
        self.open_state = OpenState.open

    def on_opening(self, _instance, _value):
        Logger.info("Opening drawer")
        if self._anim:
            self._anim.cancel(self)
            self._anim = None
        self._anim = Animation(
            size_hint_x=self.size_hint_x_open,
            duration=self.animation_open_duration,
            t="out_quad",
        )

        self._anim.bind(on_complete=partial(self.dispatch, "on_open"))

        # Keep our menu button in a static position
        self._menu_button.pos_hint = {"left": 0, "top": 1}
        self._anim.start(self)

    def on_closing(self, _instance, _value):
        Logger.info("Closing drawer")
        if self._anim:
            self._anim.cancel(self)
            self._anim = None

        self._anim = Animation(
            size_hint_x=self.size_hint_x_closed,
            duration=self.animation_close_duration,
            t="out_quad",
        )
        self._anim.bind(on_complete=partial(self.dispatch, "on_close"))
        self._anim.start(self)

    def on_close(self, _instance, _value):
        Logger.info("Drawer opened")
        self._anim = None
        self._menu_button.pos_hint = self._menu_button_pos_hint_closed
        self.open_state = OpenState.closed

    def toggle(self, _instance):
        match self.open_state:
            case OpenState.open:
                self.on_open_state(self, OpenState.closing)
            case OpenState.closed:
                self.on_open_state(self, OpenState.opening)
            case OpenState.opening:
                self.on_open_state(self, OpenState.closing)
            case OpenState.closing:
                self.on_open_state(self, OpenState.opening)
