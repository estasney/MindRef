from functools import partial
from typing import Literal

from kivy.animation import Animation
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.anchorlayout import AnchorLayout

from mindref.lib.utils import import_kv

OPEN_STATE = Literal["open", "closed", "opening", "closing"]

import_kv(__file__)


class DrawerLayout(AnchorLayout):
    """
    A layout that mimics the behavior of a drawer component.

    The drawer is anchored to the left side of the screen and begins offscreen (hidden).
    When the drawer is opened, it slides into view from the left side of the screen.
    When the drawer is closed, it slides offscreen to the left.

    Attributes
    ----------
    auto_dismiss: BooleanProperty
        If True, the drawer will dismiss itself when the user taps outside of the drawer.
    background_color: ColorProperty
        The color of the background of the drawer.
    overlay_color: ColorProperty
        The color of the overlay that is displayed when the drawer is open. Can be used to dim the window behind the drawer.
    overlay_alpha: NumericProperty
        The alpha value of the overlay that is displayed when the drawer is open. Can be used to dim the window behind the drawer.
    is_open: AliasProperty
        True if the drawer is open, False otherwise.
    content: ObjectProperty
        The content of the drawer. Internally, this will call self.add_widget() to add the content to the drawer.
    anim_duration: NumericProperty
        The duration of the animation when opening or closing the drawer.
    _open_state: OptionProperty
        The current state of the drawer. Can be one of the following:
            'closed': The drawer is closed and offscreen.
            'open': The drawer is open and onscreen.
            'opening': The drawer is opening and sliding into view.
            'closing': The drawer is closing and sliding offscreen.
    _anim_alpha: NumericProperty
        The current alpha value of the overlay.
    _window: ObjectProperty
    _window_size: AliasProperty
    _touch_started_inside: BooleanProperty


    """

    auto_dismiss = BooleanProperty(True)
    background_color = ColorProperty()
    overlay_color = ColorProperty()
    overlay_alpha = NumericProperty(0.95)
    content = ObjectProperty(None, allownone=True)
    anim_duration = NumericProperty(0.2)
    _open_state: OPEN_STATE = OptionProperty(
        "closed", options=("closed", "open", "closing", "opening")
    )
    _anim = ObjectProperty(None, allownone=True)
    _anim_alpha = NumericProperty(0)
    _window = ObjectProperty(None, allownone=True)
    _touch_started_inside = None

    __events__ = ("on_opening", "on_open", "on_closing", "on_close")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_opening")
        self.register_event_type("on_open")
        self.register_event_type("on_closing")
        self.register_event_type("on_close")

    def _get_is_open(self):
        return self._open_state == "open"

    is_open = AliasProperty(_get_is_open, None, bind=("_open_state",), cache=True)

    def _get_window_size(self):
        if self._window:
            return self._window.size
        return 0, 0

    _window_size = AliasProperty(_get_window_size, None, bind=("_window",), cache=True)

    def open(self, *_args, **kwargs):
        """
        Display the drawer in the Window

        When the drawer is opened, it slides into view from the left side of the screen.

        """

        from kivy.core.window import Window

        if self.is_open:
            return
        self._window = Window
        Window.add_widget(self, 0)
        self.right = 0
        self.dispatch("on_opening")

    def close(self, *_args, **kwargs):
        """
        Close the drawer

        When the drawer is closed, it slides offscreen to the left.

        """
        if not self.is_open:
            return
        self.dispatch("on_closing")

    def on_opening(self, *_args):
        """Setup animation to slide in drawer from left side of screen"""
        self._anim = Animation(
            right=self.width + self.padding[0], duration=self.anim_duration
        ) + Animation(_anim_alpha=self.overlay_alpha, duration=self.anim_duration)
        self._anim.bind(on_complete=partial(self.dispatch, "on_open"))
        self._anim.start(self)
        self._open_state = "opening"

    def on_closing(self, *_args):
        """Setup animation to slide in drawer from left side of screen to offscreen"""
        funbind = self.funbind
        funbind("x", self._align_to_window)
        funbind("width", self._align_to_window)
        funbind("size", self._align_to_window)
        self._anim = Animation(_anim_alpha=0, duration=self.anim_duration, right=0)
        self._anim.bind(on_complete=partial(self.dispatch, "on_close"))
        self._anim.start(self)

    def on_open(self, *_args):
        """Set state to 'open', and listen for Window resize events"""
        self._anim = None
        self._open_state = "open"
        fbind = self.fbind
        fbind("x", self._align_to_window)
        fbind("width", self._align_to_window)
        fbind("size", self._align_to_window)

    def on_close(self, *_args):
        """Set state to 'closed', and stop listening for Window resize events"""
        if self._window:
            self._window.remove_widget(self)
            self._window = None
        self._anim = None
        self._open_state = "closed"

    def _align_to_window(self, *_args):
        if self.is_open:
            self.right = self.width + self.padding[0]

    def on_content(self, _instance, value):
        if value:
            self.clear_widgets()
            self.add_widget(value)
        else:
            self.clear_widgets()

    def on_motion(self, etype, me):
        super().on_motion(etype, me)
        return True

    def on_touch_down(self, touch):
        self._touch_started_inside = self.collide_point(*touch.pos)
        if not self.auto_dismiss or self._touch_started_inside:
            super().on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        if not self.auto_dismiss or self._touch_started_inside:
            super().on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        if self.auto_dismiss or self._touch_started_inside is False:
            self.close()
        else:
            super().on_touch_up(touch)
        self._touch_started_inside = None
        return True
