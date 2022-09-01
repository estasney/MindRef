from __future__ import annotations

from typing import Any, Literal, NamedTuple, Optional

from kivy.cache import Cache
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
)
from kivy.uix.label import Label
from kivy.utils import escape_markup

Cache.register("color_norm", limit=1000)
Cache.register("text_contrast", limit=1000)

from utils.caching import cache_key_color_norm, cache_key_text_contrast, kivy_cache

from utils import import_kv

import_kv(__file__)


class TextSnippet(NamedTuple):
    text: str
    highlight_tag: Optional[Literal["hl", "kbd"]]


class LabelHighlightInline(Label):
    """
    Useful for instances where text has inline highlighting. In other words, the text snippet is highlighted at the
    character level. The main difference is in how the extents are computed.

    Attributes
    ----------
    bg_color: ColorProperty
        Refers to the color it is drawn on top of
    highlight_color: ColorProperty
        Refers to the color applied for highlighting
    kbd_color: ColorProperty
        Refers to the color applied for highlighting `<kbd>` tags (keyboard)
    kbd_shadow_color: ColorProperty
        Refers to the shadow applied for <kbd> tags
    text_threshold: NumericProperty
        'Magic' number that determines when text should be black/white
    text_color: StringProperty
        Refers to the computed contrast color for non-highlighted text
    text_color_highlight: StringProperty
        Refers to the computed contrast color for highlighted text
    snippets: ListProperty
        List of `TextSnippet`
    has_parent: BooleanProperty
    highlight_padding_x : NumericProperty
        Additional width to add to a highlighted text ref
    highlight_padding_y: NumericProperty
        Additional height to add to a highlighted text ref
    highlight_padding: ReferenceListProperty
        Additional width and height of a highlighted text ref's highlight
    """

    bg_color = ColorProperty()
    highlight_color = ColorProperty()
    kbd_color = ColorProperty()
    kbd_shadow_color = ColorProperty()
    text_threshold = NumericProperty(defaultvalue=186)
    text_color = StringProperty("#ffffff")
    text_color_highlight = StringProperty("#ffffff")
    font_family_normal = StringProperty()
    font_family_mono = StringProperty()
    snippets: list[TextSnippet] = ListProperty()
    has_parent: BooleanProperty(defaultvalue=False)
    highlight_padding_x = NumericProperty(defaultvalue=0)
    highlight_padding_y = NumericProperty(defaultvalue=0)
    highlight_padding = ReferenceListProperty(highlight_padding_x, highlight_padding_y)

    def __init__(self, **kwargs):
        super(LabelHighlightInline, self).__init__(**kwargs)
        self.markup_text_trigger = Clock.create_trigger(self.markup_text)
        self.handle_contrast_trigger = Clock.create_trigger(self.handle_contrast)
        self.draw_ref_spans_trigger = Clock.create_trigger(self.draw_ref_spans)

    def on_parent(self, instance, value):
        fbind = self.fbind
        funbind = self.funbind
        if self.parent:
            fbind("text_color", self.markup_text_trigger)
            fbind("text_color_highlight", self.markup_text_trigger)
            fbind("bg_color", self.handle_contrast_trigger)
            fbind("text_threshold", self.handle_contrast_trigger)
            fbind("snippets", self.markup_text_trigger)
            fbind("refs", self.draw_ref_spans_trigger)
            fbind("size", self.draw_ref_spans_trigger)
            fbind("pos", self.draw_ref_spans_trigger)
            fbind("padding_x", self.draw_ref_spans_trigger)
            fbind("padding_y", self.draw_ref_spans_trigger)

        else:
            funbind("text_color", self.markup_text_trigger)
            funbind("text_color_highlight", self.markup_text_trigger)
            funbind("bg_color", self.handle_contrast_trigger)
            funbind("text_threshold", self.handle_contrast_trigger)
            funbind("snippets", self.markup_text_trigger)
            funbind("refs", self.draw_ref_spans_trigger)
            funbind("size", self.draw_ref_spans_trigger)
            funbind("pos", self.draw_ref_spans_trigger)
            funbind("padding_x", self.draw_ref_spans_trigger)
            funbind("padding_y", self.draw_ref_spans_trigger)

    def add_snippet(self, snippet: TextSnippet):
        self.snippets.append(snippet)

    def handle_contrast(self, *args, **kwargs):
        """Update computed text_colors"""
        self.text_color = get_cached_text_contrast(
            background_color=self.bg_color,
            threshold=self.text_threshold,
            highlight_color=None,
        )
        self.text_color_highlight = get_cached_text_contrast(
            background_color=self.bg_color,
            threshold=self.text_threshold,
            highlight_color=self.highlight_color,
        )
        return True

    def markup_text(self, *args, **kwargs):
        """Update the markup within text to reflect new colors"""
        texts = []
        for snippet in self.snippets:
            # If our last snippet is highlighted we add additional
            snippet_text = snippet.text
            if snippet.highlight_tag == "hl":
                snippet_text = escape_markup(snippet_text)
                texts.append(
                    f" [font={self.font_family_mono}]"
                    f"[color={self.text_color_highlight}]"
                    f"[ref=hl]{snippet_text}[/ref][/color][/font] "
                )
            elif snippet.highlight_tag == "kbd":
                snippet_text = escape_markup(snippet_text)
                texts.append(
                    f" [font={self.font_family_mono}]"
                    f"[color=#000000]"
                    f"[ref=kbd]{snippet_text}[/ref][/color][/font] "
                )
            else:
                texts.append(
                    f"[color={self.text_color}]{escape_markup(snippet_text)}[/color]"
                )

        # Snippets preserve leading/trailing whitespace
        self.text = "".join(texts)
        return True

    def compute_ref_coords(
        self, span: tuple[int, int, int, int]
    ) -> tuple[float, float, float, float]:
        """
        Since spans are computed relative to texture, we want them in window form

        Spans (x1, y1) references the top left corner of the texture
        Spans y2 increases as it moves down

        Kivy's typical origin is (0,0) at bottom-left.

        ┌───────────────────────────────────────────────────────────────────────┐
        │                                 Parent                                │
        │   ┌───────────────────────────────────────────────────────────────┐   │
        │   │                             Label                             │   │
        │   │                                                               │   │
        │   │   ┌────────────────────────────────────────────────────────┐  │   │
        │   │   │                                                        │  │   │
        │   │   │                        Texture                         │  │   │
        │   │   └────────────────────────────────────────────────────────┘  │   │
        │   │                                                               │   │
        │   └───────────────────────────────────────────────────────────────┘   │
        │                                                                       │
        │                                                                       │
        └───────────────────────────────────────────────────────────────────────┘


        Parameters
        ----------
        span

        Returns
        -------

        """
        # Window X coordinate of left edge of text texture

        pX = self.center_x - self.texture_size[0] / 2

        # Window Y coordinate of bottom edge of text texture

        pY = self.center_y - self.texture_size[1] / 2

        x1, y1, x2, y2 = span

        x1 += pX
        y1 += pY
        x2 += pX
        y2 += pY

        # Padding
        x1 -= self.highlight_padding_x
        x2 += self.highlight_padding_x
        y1 += self.highlight_padding_y
        y2 -= self.highlight_padding_y

        return x1, y1, x2, y2

    def draw_ref_spans(self, *args, **kwargs):
        """
        Draw ref highlights

        Notes
        ------
        These have a bounding box at (x1, y1, x2, y2).
        These coordinates are relative to the top left corner of the text, with the y value increasing downwards.
        """
        if not self.refs:
            with self.canvas.before:
                self.canvas.before.clear()
            return
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*self.highlight_color)

            for span in self.refs.get("hl", []):
                x1, y1, x2, y2 = self.compute_ref_coords(span)
                w = x2 - x1
                h = y2 - y1
                RoundedRectangle(pos=(x1, y1), size=(w, h), radius=(3,))

            kbd_inset_x = dp(0.75)
            kbd_inset_y = dp(0.75)
            for span in self.refs.get("kbd", []):
                x1, y1, x2, y2 = self.compute_ref_coords(span)
                w = x2 - x1
                h = y2 - y1
                # darker background
                Color(*self.kbd_shadow_color)
                RoundedRectangle(
                    pos=(x1 - kbd_inset_x, y1 - kbd_inset_y),
                    size=(w, h),
                    radius=(3,),
                )
                Color(*self.kbd_color)
                RoundedRectangle(
                    pos=(x1 + kbd_inset_x, y1 + kbd_inset_y),
                    size=(w - kbd_inset_x, h - (1 * kbd_inset_y)),
                    radius=(3,),
                )


@kivy_cache(cache_name="text_contrast", key_func=cache_key_text_contrast)
def get_cached_text_contrast(
    *,
    background_color: tuple[float],
    threshold: float,
    highlight_color: Optional[Any] = None,
):
    """
    Set text as white or black depending on bg
    """
    if not highlight_color:
        r, g, b, opacity = get_cached_color_norm(color=background_color)
        brightness = (r * 0.299 + g * 0.587 + b * 0.114 + (1 - opacity)) * 255
    else:
        hl_norm = get_cached_color_norm(color=highlight_color)
        bg_norm = get_cached_color_norm(color=background_color)

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


@kivy_cache(cache_name="color_norm", key_func=cache_key_color_norm)
def get_cached_color_norm(color) -> tuple[float, float, float, float]:
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
