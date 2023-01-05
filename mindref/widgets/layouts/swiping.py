from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.transformation import Matrix
from kivy.metrics import dp
from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    AliasProperty,
    BooleanProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter

from utils import import_kv, schedulable

import_kv(__file__)


class LabeledBoundsLayout(FloatLayout):
    """A FloatLayout with Labels for swipe bounds"""

    swipe_threshold = NumericProperty(dp(50))
    swiping = BooleanProperty(False)


class SwipingLayout(Scatter):
    """
    Class that allows the user to swipe a widget partially off the screen in the x axis.

    Events
    ------
    on_swipe: (swipe_direction: bool)
        Fired when the widget is swiped off the screen. swipe_direction is True if widget was swiped to the right, False otherwise.

    Attributes
    ----------
    content: ObjectProperty
        Similar to `ScatterLayout.content`, We use a `FloatLayout` to hold the widget that we want to swipe.
        Widgets are not added directly to the `SwipingLayout`, but to the content `FloatLayout`.
    swipe_threshold: NumericProperty
        The widget must be moved `swipe_threshold` * `self.width` before it is considered swiped off the screen.
        This also limits how far the widget can be translated in the x-axis.
    min_translation: NumericProperty
        The minimum translation in the x-axis before we begin to translate the widget. This is to prevent jittering.
    _last_touch_pos_x: NumericProperty
        The x position of the last touch event.
    _swipe_width: AliasProperty
        The width of the widget when it is considered swiped off the screen.
    """

    __events__ = ("on_swipe",)

    content = ObjectProperty()
    swipe_threshold = NumericProperty(0.15)
    min_translation = NumericProperty(dp(20))
    _last_touch_pos_x = NumericProperty(0)

    def __init__(self, **kwargs):
        # We need to add content here instead of in the kv file as we've overridden add_widget
        self.content = LabeledBoundsLayout(size_hint=(None, None))

        super().__init__(
            **{
                **kwargs,
                **dict(do_translation=False, do_scale=False, do_rotation=False),
            }
        )
        if self.content.size != self.size:
            self.content.size = self.size

        super().add_widget(self.content)
        fbind = self.fbind
        fbind("size", self.content.setter("size"))
        fbind("_swipe_width", self.content.setter("swipe_threshold"))
        fbind("swiping", self.content.setter("swiping"))

        self.animate_snap_back = Animation(
            x=0, d=0.2, _last_touch_pos_x=0, t="out_quad"
        )

        self.register_event_type("on_swipe")

    def _get_swipe_width(self):
        return self.swipe_threshold * self.width

    _swipe_width = AliasProperty(
        _get_swipe_width, None, bind=("swipe_threshold", "width"), cache=True
    )

    def _get_swiping(self):
        return self._last_touch_pos_x != 0

    swiping = AliasProperty(_get_swiping, None, bind=("_last_touch_pos_x",))

    def on_swipe(self, swipe_direction: bool):
        ...

    def add_widget(self, *args, **kwargs):
        self.content.add_widget(*args, **kwargs)

    def remove_widget(self, *args, **kwargs):
        self.content.remove_widget(*args, **kwargs)

    def clear_widgets(self, *args, **kwargs):
        self.content.clear_widgets(*args, **kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Cancel any animations that are currently running
            self.animate_snap_back.cancel(self)
            touch.grab(self)
            self._last_touch_pos_x = touch.x
            self.dispatch_children("on_touch_down", touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):

        if touch.grab_current is self:
            # Calculate the delta between the last touch event and this one
            x_touch = touch.x
            dX = x_touch - self._last_touch_pos_x
            has_moved = abs(dX) > self.min_translation

            self.dispatch_children("on_touch_down", touch)
            if not has_moved:
                return False

            # We can physically move the widget now
            # We need to clamp the delta to avoid moving past the swipe threshold

            # Calculate the new x position of the widget
            new_x = self.x + dX
            # Calculate if this new position is past the swipe threshold
            past_threshold = abs(new_x) - self._swipe_width
            # If it is, we need to clamp the delta to prevent moving past the threshold
            if past_threshold > 0:
                dX -= past_threshold if new_x > 0 else -past_threshold

            self._last_touch_pos_x = x_touch
            self.apply_transform(Matrix().translate(dX, 0, 0))

        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # Determine if the widget meets the swipe threshold
            if abs(self.x) >= (self._swipe_width * 0.95):
                dispatch = schedulable(self.dispatch, "on_swipe", self.x > 0)
                Clock.schedule_once(dispatch, timeout=self.animate_snap_back.duration)
            self.animate_snap_back.start(self)
        return super().on_touch_up(touch)
