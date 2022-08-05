import re
from typing import NamedTuple

from kivy import Logger
from kivy.metrics import sp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.label import Label
from kivy.utils import escape_markup

from utils import import_kv
from widgets.behavior.label_behavior import get_cached_text_contrast

import_kv(__file__)


class TextSnippet(NamedTuple):
    text: str
    highlight: bool


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
    text_threshold: NumericProperty
        'Magic' number that determines when text should be black/white
    text_color: StringProperty
        Refers to the computed contrast color for non-highlighted text
    text_color_highlight: StringProperty
        Refers to the computed contrast color for highlighted text
    snippets: ListProperty
        List of `TextSnippet`
    """

    bg_color = ColorProperty()
    highlight_color = ColorProperty()
    text_threshold = NumericProperty(defaultvalue=186)
    text_color = StringProperty("#ffffff")
    text_color_highlight = StringProperty("#ffffff")
    font_family_normal = StringProperty()
    font_family_mono = StringProperty()
    snippets: list[TextSnippet] = ListProperty()
    has_parent: BooleanProperty(defaultvalue=False)

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

        # Add one additional whitespace for highlight snippets ending in 'newline'
        RE_NEWLINE_PAD = re.compile(r"(?<=\S)(\n)|(\r\n)")

        texts = []
        for snippet in self.snippets:
            if snippet.highlight:
                snippet_text = RE_NEWLINE_PAD.sub(" \n", escape_markup(snippet.text))
                texts.append(
                    f"[font={self.font_family_mono}]"
                    f"[color={self.text_color_highlight}]"
                    f"[ref=hl] {snippet_text} [/ref][/color][/font]"
                )
            else:
                texts.append(
                    f"[color={self.text_color}]{escape_markup(snippet.text)}[/color]"
                )

        # Snippets preserve leading/trailing whitespace
        self.text = "".join(texts)
        return True

    def compute_ref_coords(
        self, span: tuple[int, int, int, int]
    ) -> tuple[float, float, float, float]:
        """
        Since spans are computed relative to texture, we want them in window form

        Kivy's origin is (0,0) at bottom-left

        Parameters
        ----------
        span

        Returns
        -------

        """

        # Window X coordinate of top left text texture
        pX = self.x + self.padding_x

        # Window Y coordinate of top left text texture
        pY = self.y + self.padding_y + self.texture_size[1]
        # pY = self.padding_y + self.y + self.height

        x1, y1, x2, y2 = span
        x1 += pX
        y1 = pY - y1

        x2 += pX
        y2 = pY - y2

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

            for span in self.refs.get("hl"):
                x1, y1, x2, y2 = self.compute_ref_coords(span)
                w = x2 - x1
                h = y2 - y1
                RoundedRectangle(pos=(x1, y1), size=(w, h), radius=(3,))
