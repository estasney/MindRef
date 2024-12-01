from kivy.animation import Animation
from kivy.properties import (
    ColorProperty,
    BooleanProperty,
    NumericProperty,
    AliasProperty,
)
from kivy.uix.widget import Widget

from lib.utils import import_kv

import_kv(__file__)


class Separator(Widget):
    color = ColorProperty()
    ...


class HSeparator(Separator):
    ...


class VSeparator(Separator):
    ...


class AnimatedHSeparator(HSeparator):
    """
    A horizontal separator that animates its width and color when its `active` property is set to True.

    Attributes
    ----------
    active: bool
        Whether the separator is active or not. When active, the separator's width will be its inactive width * a modifier.
        And its color will be its active color
    width_modifier: float
        The modifier to apply to the inactive width when the separator is active
    color: ColorProperty
        The color of the separator when it is inactive
    active_color: ColorProperty
        The color to apply to the separator when it is active
    animation_duration: float
        The duration of the animation when the separator is activated/deactivated
    _width: float
        The width of the separator when it is inactive. Since we are animating the width, we need to keep a reference to it
    _color: ColorProperty
        The color of the separator when it is inactive. Since we are animating the color, we need to keep a reference to it
    """

    active = BooleanProperty(False)
    width_modifier = NumericProperty(1.5)
    active_color = ColorProperty()
    animation_duration = NumericProperty(0.2)
    _width = NumericProperty()
    _color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_animation_active(self):
        self._width = self.width
        self._color = self.color
        return Animation(
            width=self._width * self.width_modifier,
            color=self.active_color,
            duration=self.animation_duration,
        )

    def get_animation_inactive(self):
        return Animation(
            width=self._width, color=self._color, duration=self.animation_duration
        )

    animation_active = AliasProperty(
        get_animation_active,
        None,
        bind=("_width", "width_modifier", "active_color", "animation_duration"),
    )
    animation_inactive = AliasProperty(
        get_animation_inactive, None, bind=("_width", "_color", "animation_duration")
    )

    def on_active(self, _instance, value):
        if value:
            self.animation_active.start(self)
        else:
            self.animation_inactive.start(self)
