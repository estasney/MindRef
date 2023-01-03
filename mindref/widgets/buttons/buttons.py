from kivy.properties import (
    ColorProperty,
    StringProperty,
    VariableListProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv, mindref_path
from utils.calculation import normalize_coordinates
from widgets.effects.ripple import RippleMixin

texture_atlas = "atlas://" + str(mindref_path() / "static" / "textures" / "textures")
icon_atlas = "atlas://" + str(mindref_path() / "static" / "icons" / "icons")
import_kv(__file__)


class ThemedButton(ButtonBehavior, BoxLayout, RippleMixin):
    """
    Base class for all MindRef themed buttons. By itself, it is an empty BoxLayout
    """

    background_normal = StringProperty(f"{texture_atlas}/bg_normal")
    background_down = StringProperty(f"{texture_atlas}/bg_down")
    background_disabled = StringProperty(f"{texture_atlas}/bg_disabled")
    background_color = ColorProperty()
    border = VariableListProperty()
    enable_ripple_effect = BooleanProperty(True)

    def __init__(self, **kwargs):
        self._on_touch_down_plain = super().on_touch_down
        self._on_touch_move_plain = super().on_touch_move
        self._on_touch_up_plain = super().on_touch_up
        super(ThemedButton, self).__init__(**kwargs)
        self.bind(enable_ripple_effect=self.toggle_ripple_effect)
        self.toggle_ripple_effect()

    def normalize_touch_pos(self, touch_x, touch_y):
        """
        Normalize touch position to texture coordinates.

        Kivy's origin point is the bottom left corner of the window.


        """
        return normalize_coordinates(
            touch_x,
            touch_y,
            self.x,
            self.y,
            self.height - self.border[0] - self.border[2],
            self.width - self.border[1] - self.border[3],
        )

    def toggle_ripple_effect(self, *_args):
        if self.enable_ripple_effect:
            setattr(self, "on_touch_down", self._on_touch_down_ripple)
            setattr(self, "on_touch_move", self._on_touch_move)
            setattr(self, "on_touch_up", self._on_touch_up)
        else:
            setattr(self, "on_touch_down", self._on_touch_down_plain)
            setattr(self, "on_touch_move", self._on_touch_move_plain)
            setattr(self, "on_touch_up", self._on_touch_up_plain)

    def _on_touch_down_ripple(self, touch):
        if super().on_touch_down(touch):
            self.touch = self.normalize_touch_pos(*touch.pos)
            self.no_touch_trigger.cancel()
            self.has_touch_trigger()
            return True
        return False

    def _on_touch_move(self, touch):
        if super().on_touch_move(touch):
            self.touch = self.normalize_touch_pos(*touch.pos)
            return True
        return False

    def _on_touch_up(self, touch):
        super().on_touch_up(touch)
        self.has_touch_trigger.cancel()
        self.no_touch_trigger()
        return True


class ThemedLabelButton(ThemedButton):
    """Extends ThemedButton to add a label"""

    text: StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ThemedIconButton(ThemedLabelButton):
    """Extends ThemedLabelButton by replacing BaseLabel with IconLabel"""

    icon_code = StringProperty()
    icon_size = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ImageButton(ThemedButton):
    source = StringProperty()

    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)


class SaveButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/save")

    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)


class CancelButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/cancel")

    def __init__(self, **kwargs):
        super(CancelButton, self).__init__(**kwargs)
