from kivy.animation import Animation
from kivy.graphics.transformation import Matrix
from kivy.metrics import dp
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter

from mindref.lib.utils import import_kv, sch_cb, schedulable

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
    swiping: AliasProperty
        True if the widget is currently being swiped. This is defined as the widget having a non-zero transform matrix,
         and a touch event that it has grabbed.
    translation: AliasProperty
        The current translation of the widget in the x-axis. This is aliased from the transform matrix.
    _swiping: BooleanProperty
        Set to True when the widget has a touch event that it has grabbed.
    _last_touch_pos_x: NumericProperty
        The x position of the last touch event.
    _swipe_width: AliasProperty
        The width of the widget when it is considered swiped off the screen.
    """

    __events__ = ("on_swipe",)

    content = ObjectProperty()
    swipe_threshold = NumericProperty(0.15)
    min_translation = NumericProperty(dp(20))
    _swiping = BooleanProperty(False)
    _last_touch_pos_x = NumericProperty(0)
    _last_touch_pos_y = NumericProperty(0)
    _touch_translate_y = NumericProperty(0)

    def __init__(self, **kwargs):
        # We need to add content here instead of in the kv file as we've overridden add_widget
        self.content = LabeledBoundsLayout(size_hint=(None, None))

        super().__init__(
            **{
                **kwargs,
                **{"do_translation": False, "do_scale": False, "do_rotation": False},
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
        self.animate_snap_back.bind(on_complete=self._on_snap_back_complete)

        self.register_event_type("on_swipe")

    def _on_snap_back_complete(self, *args):
        self._last_touch_pos_x = 0
        self._swiping = False

    def _get_swipe_width(self):
        return self.swipe_threshold * self.width

    _swipe_width = AliasProperty(
        _get_swipe_width, None, bind=("swipe_threshold", "width"), cache=True
    )

    def _get_swiping(self):
        return self._swiping or abs(self.translation) > self.min_translation

    swiping = AliasProperty(
        _get_swiping,
        None,
        bind=("_swiping", "translation", "min_translation"),
        cache=True,
    )

    def _get_translation(self):
        return self.transform.get()[12]

    translation = AliasProperty(
        _get_translation,
        None,
        bind=("transform",),
        cache=True,
    )

    def on_swipe(self, swipe_direction: bool): ...

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
            self._last_touch_pos_y = touch.y
            self._touch_translate_y = 0
            self.dispatch_children("on_touch_down", touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            x_touch, y_touch = touch.pos
            curr_trans = self.translation
            x_last = self._last_touch_pos_x
            y_last = self._last_touch_pos_y
            self._last_touch_pos_y = y_touch

            # Update our total y translation
            self._touch_translate_y += y_touch - y_last

            # First determine if we should be moving the widget, by checking if this touch event would move us past the min_translation
            delta_x = x_touch - x_last

            if abs(curr_trans + delta_x) < self.min_translation:
                # We haven't moved past the minimum translation, so we don't activate swiping display behavior
                return None

            # We may have moved past the minimum translation, but we need to check if the user is trying to scroll vertically
            if abs(self._touch_translate_y) > self.swipe_threshold * (abs(delta_x)):
                # The user is trying to scroll vertically
                return None

            self._swiping = True

            self.dispatch_children("on_touch_down", touch)

            # We can physically move the widget now
            # We need to clamp the delta to avoid moving past the swipe threshold
            new_trans = self.translation + delta_x

            past_swipe_threshold = abs(new_trans) - self._swipe_width

            if past_swipe_threshold > 0:
                delta_x -= (
                    past_swipe_threshold if new_trans > 0 else -past_swipe_threshold
                )

            self._last_touch_pos_x = x_touch
            self.apply_transform(Matrix().translate(delta_x, 0, 0))

        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # Determine if the widget meets the swipe threshold
            if abs(self.x) >= (self._swipe_width * 0.95):
                dispatch = schedulable(self.dispatch, "on_swipe", self.x > 0)

                sch_cb(dispatch, timeout=0.1)
            self.animate_snap_back.start(self)
        return super().on_touch_up(touch)
