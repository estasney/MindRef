from typing import NamedTuple

from kivy.graphics import Color, RoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.label import Label

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

    def on_parent(self, instance, value):
        fbind = self.fbind
        funbind = self.funbind
        if self.parent:
            fbind("text_color", self.markup_text)
            fbind("text_color_highlight", self.markup_text)
            fbind("bg_color", self.handle_contrast)
            fbind("text_threshold", self.handle_contrast)
            fbind("snippets", self.markup_text)
            fbind("refs", self.draw_ref_spans)
            fbind("size", self.draw_ref_spans)
            fbind("pos", self.draw_ref_spans)

        else:
            funbind("text_color", self.markup_text)
            funbind("text_color_highlight", self.markup_text)
            funbind("bg_color", self.handle_contrast)
            funbind("text_threshold", self.handle_contrast)
            funbind("snippets", self.markup_text)
            funbind("refs", self.draw_ref_spans)
            funbind("size", self.draw_ref_spans)
            funbind("pos", self.draw_ref_spans)

    def add_snippet(self, snippet: TextSnippet):
        self.snippets.append(snippet)

    def handle_contrast(self, instance, value):
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

    def markup_text(self, instance, value):
        """Update the markup within text to reflect new colors"""

        texts = []
        for snippet in self.snippets:
            if snippet.highlight:
                texts.append(
                    f"[font={self.font_family_mono}][color={self.text_color_highlight}][ref=hl] {snippet.text} [/ref][/color][/font]"
                )
            else:
                texts.append(f"[color={self.text_color}]{snippet.text}[/color]")

        # Snippets preserve leading/trailing whitespace
        self.text = "".join(texts)
        return True

    def draw_ref_spans(self, instance, value):
        """Draw ref highlights"""
        if not self.refs:
            return
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*self.highlight_color)
            for span in self.refs.get("hl"):
                x1, y1, x2, y2 = span
                w = x2 - x1
                h = y2 - y1
                xp, yp = self.to_parent(x1, y2)
                if w + self.x + xp >= self.width:
                    w += 4

                RoundedRectangle(
                    pos=(self.x + xp, self.y + yp), size=(w, h), radius=(3,)
                )
