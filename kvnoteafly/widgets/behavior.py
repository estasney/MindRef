from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
)
from kivy.uix.label import Label
import re

RE_COLOR_HEAD = re.compile(r"\[color=#[A-z\d]{6}]")
RE_COLOR_TAIL = re.compile(r"\[/color]")


class LabelBG(Label):
    """Label that draws background sized to extents if bg_enabled is set True"""

    y_extent = NumericProperty()
    x_extent = NumericProperty()
    extents = ReferenceListProperty(x_extent, y_extent)
    bg_enabled = BooleanProperty(False)
    bg_color = ColorProperty()
    text_color = StringProperty("#ffffff")
    text_threshold = NumericProperty(186)

    def __init__(self, text, **kwargs):
        if self.bg_enabled or kwargs.get("bg_enabled"):
            kwargs.update({"text": f"[color={self.text_contrast()}]{text}[/color]"})
        else:
            kwargs.update({"text": text})
        super(LabelBG, self).__init__(**kwargs)

    def on_bg_enabled(self, instance, value):
        if not value:
            self.unbind(texture_size=self.get_extents)
        else:
            self.text_contrast()

            self.bind(texture_size=self.get_extents)

    def text_contrast(self, *args, **kwargs):
        """
        Set text as white or black depending on bg

        """
        if hasattr(self.bg_color, "startswith"):
            color_string = self.bg_color.removeprefix("#")
            r, g, b, = (
                int(color_string[:2], 16),
                int(color_string[2:4], 16),
                int(color_string[4:6], 16),
            )

        else:
            r, g, b, *_ = self.bg_color
            r *= 255
            g *= 255
            b *= 255

        # https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
        if (r * 0.299 + g * 0.587 + b * 0.114) > self.text_threshold:
            return "#000000"
        else:
            return "#ffffff"

    def get_extents(self, instance, value):
        # Texture created
        # We have to remove markup
        l_text = RE_COLOR_TAIL.sub("", RE_COLOR_HEAD.sub("", self.text))
        w, h = self._label.get_extents(l_text)

        # Now we can draw our codespan background
        self.x_extent = w + (2 * self.padding_x)
        self.y_extent = h + self.padding_y

    def on_extents(self, instance, value):
        Clock.schedule_once(self.draw_bg_extents)

    def get_x(self):
        if self.halign == "left":
            return self.center_x - self.texture_size[0] * 0.5
        elif self.halign == "center":
            return self.center_x - self.x_extent * 0.5
        elif self.halign == "right":
            return self.texture_size[0] - self.x_extent + (4 * self.padding_x)
        else:
            return self.center_x

    def get_y(self):
        return (self.center_y - self.texture_size[1] * 0.5) + (self.padding_y * 0.5)

    def draw_bg_extents(self, *args, **kwargs):
        self.canvas.before.clear()
        with self.canvas.before:

            Color(*self.bg_color)
            Rectangle(pos=(self.get_x(), self.get_y()), size=self.extents)
