from __future__ import annotations

from kivy import Logger

from utils import import_kv

import_kv(__file__)

from typing import Any, Optional
from kivy.clock import Clock
from kivy.cache import Cache
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
)
from kivy.uix.label import Label
from functools import wraps

Cache.register("color_norm", timeout=30)
Cache.register("text_contrast", timeout=30)
Cache.register("text_extents", limit=1000)


def get_cached_extents(label, text):
    opts = label.options
    label_id = f"{text}-{opts['font_size']}-{opts['font_family']}"
    cached_instance = Cache.get("text_extents", label_id)
    if cached_instance:
        return cached_instance
    result = label.get_extents(text)
    Cache.append("text_extents", label_id, result)
    return result


def cache_text_contrast(func):
    @wraps(func)
    def wrapped_text_contrast(background_color, threshold, highlight_color):
        key = (
            tuple(background_color),
            int(threshold),
            tuple(highlight_color) if highlight_color else None,
        )
        cached_instance = Cache.get("text_contrast", key)
        if cached_instance:
            return cached_instance
        result = func(background_color, threshold, highlight_color)
        Cache.append("text_contrast", key, result)
        return result

    return wrapped_text_contrast


def cached_color_norm(func):
    @wraps(func)
    def wrapped_func(color):
        key = tuple(color)
        cached_instance = Cache.get("color_norm", key)
        if cached_instance:
            return cached_instance
        result = func(color)
        Cache.append("color_norm", key, tuple(result))
        return result

    return wrapped_func


@cached_color_norm
def color_norm(color) -> tuple[float, float, float, float]:
    def color_str_components(s: str) -> tuple[float, float, float, float]:
        """Return hex as 1.0 * 4"""
        s = s.removeprefix("#")
        # Groups of two
        components_hex = zip(*[iter(s)] * 2)
        has_opacity = False
        for i, comp in enumerate(components_hex):
            if i == 3:
                has_opacity = True
                yield int("".join(comp), 16) / 255
                continue
            yield int("".join(comp), 16) / 255
        if not has_opacity:
            yield 1.0

    def color_float_components(
        s: tuple[int] | tuple[float],
    ) -> tuple[float, float, float, float]:
        """Return r, g, b (0.0-1.0) as (0-1) and opacity as (0-1)"""
        has_opacity = False
        for i, comp in enumerate(s):
            if i == 3:
                has_opacity = True
                yield comp
                continue
            yield comp
        if not has_opacity:
            yield 1.0

    if isinstance(color, str):
        components = color_str_components(color)
    else:
        components = color_float_components(color)

    return tuple(components)


@cache_text_contrast
def text_contrast(background_color, threshold, highlight_color: Optional[Any] = None):
    """
    Set text as white or black depending on bg

    """
    if not highlight_color:
        r, g, b, opacity = color_norm(background_color)
        brightness = (r * 0.299 + g * 0.587 + b * 0.114 + (1 - opacity)) * 255
    else:
        hl_norm = color_norm(highlight_color)
        bg_norm = color_norm(background_color)

        r_hl, g_hl, b_hl, opacity_hl = hl_norm
        r_bg, g_bg, b_bg, opacity_bg = bg_norm

        # https://stackoverflow.com/questions/726549/algorithm-for-additive-color-mixing-for-rgb-values
        opacity = 1 - (1 - opacity_hl) * (1 - opacity_bg)
        r = r_hl * opacity_hl / opacity + r_bg * opacity_bg * (1 - opacity_hl) / opacity
        g = g_hl * opacity_hl / opacity + g_bg * opacity_bg * (1 - opacity_hl) / opacity
        b = b_hl * opacity_hl / opacity + b_bg * opacity_bg * (1 - opacity_hl) / opacity

        # https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
        brightness = (r * 0.299 + g * 0.587 + b * 0.114 + (1 - opacity)) * 255
    if brightness > threshold:
        return "#000000"
    else:
        return "#ffffff"


class LabelAutoContrast(Label):
    """
    Label that changes text color to optimize contrast

    Attributes
    ----------
    bg_color: ColorProperty
        Refers to the color it is drawn on top of.
    text_color: StringProperty
    text_threshold: NumericProperty, defaults to 186
    raw_text: StringProperty
        Update text content with raw_text
    """

    bg_color = ColorProperty()
    text_color = StringProperty("#ffffff")
    text_threshold = NumericProperty(186)
    raw_text = StringProperty()

    def __init__(self, **kwargs):
        if "text" in kwargs:
            text = kwargs.pop("text")
        else:
            text = ""
        super().__init__(**kwargs)
        self.raw_text = text
        self.bind(raw_text=self.handle_raw_text)
        self.bind(bg_color=self.handle_bg_color)
        self.bind(text_color=self.handle_text_color)

    def handle_bg_color(self, instance, value):
        """When bg_color is set we set our text_color accordingly"""
        self.text_color = text_contrast(self.bg_color, self.text_threshold, None)
        return True

    def handle_text_color(self, instance, value):
        """With text_color updated, we update our text with markup"""
        self.text = f"[color={self.text_color}]{self.raw_text}[/color]"
        return True

    def handle_raw_text(self, instance, value):
        """Wrap our raw_text with text_color"""
        self.text = f"[color={self.text_color}]{value}[/color]"
        return True


class LabelHighlight(LabelAutoContrast):
    """
    Label that adds highlighting functionality

    Attributes
    ----------
    y_extent : The extent of the text in the y-axis
    x_extent : The extent of the text in the x-axis
    extents: ReferenceListProperty of x_extent, y_extent
    highlight: Toggles highlighting behavior
    highlight_color: Color of highlighting
    raw_text: Holds text before applying any markup. Required since get_extents does not remove markup.
    """

    y_extent = NumericProperty()
    x_extent = NumericProperty()
    extents = ReferenceListProperty(x_extent, y_extent)
    highlight = BooleanProperty(False)
    highlight_color = ColorProperty()

    def __init__(self, **kwargs):
        super(LabelHighlight, self).__init__(**kwargs)
        self.bind(highlight=self.handle_highlight)
        self.bind(bg_color=self.handle_bg_color)

    def handle_bg_color(self, instance, value):
        """Update our text color"""
        if self.highlight:
            self.text_color = text_contrast(
                self.bg_color, self.text_threshold, self.highlight_color
            )
        else:
            self.text_color = text_contrast(self.bg_color, self.text_threshold, None)
        return True

    def handle_highlight(self, instance, value):
        """Main switch to enable/disable behavior"""
        fbind = self.fbind
        funbind = self.funbind

        if value:
            fbind("text", self.get_extents)
            fbind("texture_size", self.get_extents)
            fbind("highlight_color", self.handle_highlight_color)
            fbind("bg_color", self.handle_bg_color)
            fbind("text_color", self.handle_text_color)
            fbind("extents", self.draw_highlight)
            fbind("pos", self.draw_highlight)
            fbind("size", self.draw_highlight)
        else:
            funbind("text", self.get_extents)
            funbind("texture_size", self.get_extents)
            funbind("highlight_color", self.handle_highlight_color)
            funbind("bg_color", self.handle_bg_color)
            funbind("text_color", self.handle_text_color)
            funbind("extents", self.draw_highlight)
            funbind("pos", self.draw_highlight)
            funbind("size", self.draw_highlight)

    def handle_highlight_color(self, instance, value):
        if self.highlight:
            self.text_color = text_contrast(
                self.bg_color, self.text_threshold, self.highlight_color
            )
            return True

    def get_extents(self, instance, value):
        """Measure the size of our text. Use cache if possible"""
        w, h = get_cached_extents(self._label, self.raw_text)

        # Now we can draw our codespan background
        self.extents = [w + (2 * self.padding_x), h + self.padding_y]
        return True

    def draw_highlight(self, instance, value):
        if self.highlight:
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
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*self.highlight_color)
            RoundedRectangle(
                pos=(self.get_x(), self.get_y()), size=self.extents, radius=(3,)
            )
