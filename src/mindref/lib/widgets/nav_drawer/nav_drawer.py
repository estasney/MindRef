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
    AliasProperty,
)
from kivy.uix.floatlayout import FloatLayout

from mindref.lib.models import AnimationTiming
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
TAnimatedProperty = Literal[
    "size_hint_x_closed",
    "size_hint_x_open",
    "animation_open_duration",
    "animation_open_timing",
    "animation_closed_duration",
    "animation_closed_timing",
]

Builder.load_string(
    """
#:import OpenMenuButton mindref.lib.widgets.buttons
#:import V2RefreshContainer mindref.lib.widgets.refreshable.refresh_container
<NavDrawer>:
    pos_hint: {"left": 0}
    FloatLayout:
        id: top_bar
        pos_hint: {"top": 1}
        size_hint_y: 0.1
        OpenMenuButton:
            id: menu_button
            size_hint: None, None
            width: self.height
            on_release: root.toggle(self)
            pos_hint: root._menu_button_pos_hint_closed
        GridLayout:
            id: side_button_grid
            opacity: 0
            cols: 2
            pos_hint: {"top": 1, "right": 1}
            width: top_bar.width - menu_button.width
            size_hint_x: None
            canvas.before:
                Color:
                    rgba: 1, 0, 0, 1  # Red color
                Line:
                    rectangle: self.x, self.y, self.width, self.height
            AnchorLayout:
                id: side_button_box
                anchor_x: "right"
                anchor_y: "center"
    V2RefreshContainer:
        id: nav_items
        size_hint_y: 0.9
        pos_hint: {"top": 0.9}
        opacity: 0
        
"""
)


class NavDrawer(FloatLayout, CustomBehavior):
    size_hint_x_closed = NumericProperty(0)
    size_hint_x_open = NumericProperty(0)
    size_hint_x = NumericProperty(0, allownone=False)
    animation_open_duration = NumericProperty(0.2)
    animation_open_timing = OptionProperty(
        AnimationTiming.in_out_quad, options=[AnimationTiming.__members__.values()]
    )
    animation_closed_duration = NumericProperty(0.2)
    animation_closed_timing = OptionProperty(
        AnimationTiming.in_out_quad, options=[AnimationTiming.__members__.values()]
    )

    animation_close_duration = NumericProperty(0.2)
    open_state = OptionProperty(
        OpenState.closed, options=list(OpenState.__members__.values())
    )

    search_button = ObjectProperty(allownone=True)

    drawer_open_animation: Animation
    drawer_close_animation: Animation
    fade_in_animation: Animation
    fade_out_animation: Animation

    _menu_button_pos_hint_closed = DictProperty({"center_x": 0.5, "center_y": 0.5})
    _menu_button_pos_hint_open = DictProperty({"left": 0, "center_y": 0.5})

    __custom_events__ = frozenset({"on_open", "on_close", "on_opening", "on_closing"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawer_open_animation = Animation(
            size_hint_x=self.size_hint_x_open,
            duration=self.animation_open_duration,
            t=self.animation_open_timing,
        )
        self.drawer_open_animation.bind(
            on_complete=lambda _: setattr(self, "open_state", OpenState.open)
        )
        self.drawer_close_animation = Animation(
            size_hint_x=self.size_hint_x_closed,
            duration=self.animation_closed_duration,
            t=self.animation_closed_timing,
        )
        self.drawer_close_animation.bind(
            on_complete=lambda _: setattr(self, "open_state", OpenState.closed)
        )
        self.fade_in_animation = Animation(
            opacity=1,
            duration=self.animation_open_duration,
            t=self.animation_open_timing,
        )
        self.fade_out_animation = Animation(
            opacity=0,
            duration=self.animation_closed_duration,
            t=self.animation_closed_timing,
        )

        self.fbind(
            "size_hint_x_closed", self.handle_animation_change, "size_hint_x_closed"
        )
        self.fbind("size_hint_x_open", self.handle_animation_change, "size_hint_x_open")
        self.fbind(
            "animation_open_duration",
            self.handle_animation_change,
            "animation_open_duration",
        )
        self.fbind(
            "animation_open_timing",
            self.handle_animation_change,
            "animation_open_timing",
        )
        self.fbind(
            "animation_closed_duration",
            self.handle_animation_change,
            "animation_closed_duration",
        )
        self.fbind(
            "animation_closed_timing",
            self.handle_animation_change,
            "animation_closed_timing",
        )

    def handle_animation_change(
        self, property_name: TAnimatedProperty, _instance, value: float
    ):
        match property_name:
            case "size_hint_x_closed":
                self.size_hint_x = value
                self.drawer_close_animation = Animation(
                    size_hint_x=value,
                    duration=self.animation_open_duration,
                    t=self.animation_open_timing,
                )
                self.drawer_close_animation.bind(
                    on_complete=lambda *_: setattr(self, "open_state", OpenState.closed)
                )
            case "size_hint_x_open":
                self.drawer_open_animation = Animation(
                    size_hint_x=value,
                    duration=self.animation_open_duration,
                    t=self.animation_open_timing,
                )
                self.drawer_open_animation.bind(
                    on_complete=lambda *_: setattr(self, "open_state", OpenState.open)
                )
            case "animation_open_duration":
                self.drawer_open_animation = Animation(
                    size_hint_x=self.size_hint_x_open,
                    duration=value,
                    t=self.animation_open_timing,
                )
                self.fade_in_animation = Animation(
                    opacity=1,
                    duration=value,
                    t=self.animation_open_timing,
                )
            case "animation_open_timing":
                self.drawer_open_animation = Animation(
                    size_hint_x=self.size_hint_x_open,
                    duration=self.animation_open_duration,
                    t=value,
                )
                self.fade_in_animation = Animation(
                    opacity=1,
                    duration=self.animation_open_duration,
                    t=value,
                )
            case "animation_closed_duration":
                self.drawer_close_animation = Animation(
                    size_hint_x=self.size_hint_x_closed,
                    duration=value,
                    t=self.animation_closed_timing,
                )
                self.fade_out_animation = Animation(
                    opacity=0,
                    duration=value,
                    t=self.animation_closed_timing,
                )
            case "animation_closed_timing":
                self.drawer_close_animation = Animation(
                    size_hint_x=self.size_hint_x_closed,
                    duration=self.animation_closed_duration,
                    t=value,
                )
                self.fade_out_animation = Animation(
                    opacity=0,
                    duration=self.animation_closed_duration,
                    t=value,
                )
            case _:
                Logger.warning(f"Unknown property: {property_name}")
                raise ValueError(f"Unknown property: {property_name}")

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
        self.open_state = OpenState.open

    def on_opening(self, _instance, _value):
        self.drawer_close_animation.cancel(self)
        self.fade_out_animation.cancel(self.ids.nav_items)
        self.ids.menu_button.pos_hint = self._menu_button_pos_hint_open
        if self.search_button is None:
            # Create a new search button
            self.search_button = ThemedIconButton(
                icon_code="\ue8b6", size_hint=(None, None), opacity=0
            )
            self.search_button.bind(height=self.search_button.setter("width"))
            self.search_button.on_release = lambda: print("Search button pressed")
            self.ids.side_button_box.add_widget(self.search_button)
        self.fade_out_animation.cancel(self.search_button)
        self.fade_in_animation.start(self.search_button)
        self.fade_in_animation.start(self.ids.nav_items)
        self.drawer_open_animation.start(self)

    def on_closing(self, _instance, _value):
        self.fade_in_animation.cancel(self.ids.nav_items)
        self.drawer_open_animation.cancel(self)
        self.fade_in_animation.cancel(self.search_button)

        self.fade_out_animation.start(self.search_button)
        self.fade_out_animation.start(self.ids.nav_items)
        self.drawer_close_animation.start(self)

    def on_close(self, _instance, _value):
        self.open_state = OpenState.closed
        self.ids.menu_button.pos_hint = self._menu_button_pos_hint_closed
        self.ids.side_button_box.remove_widget(self.search_button)
        self.search_button = None

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

    def add_widget_to_drawer(self, widget):
        self.ids.nav_items.add_widget_to_grid(widget)

    def clear_widgets_from_drawer(self):
        self.ids.nav_items.clear_widgets_from_grid()
