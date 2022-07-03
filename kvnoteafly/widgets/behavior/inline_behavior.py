from typing import Iterator, NamedTuple, Optional

from kivy import Logger
from kivy.core.text.text_layout import layout_text
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.label import Label

from utils import import_kv, sch_cb
from widgets.behavior.label_behavior import get_cached_text_contrast

import_kv(__file__)


class TextSnippet(NamedTuple):
    text: str
    highlight: bool


class HighlightSpan(NamedTuple):
    pos_x: float
    pos_y: float
    w: float
    h: float


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
    highlight_spans: list[HighlightSpan] = ListProperty()
    has_parent: BooleanProperty(defaultvalue=False)

    def __init__(self, **kwargs):
        super(LabelHighlightInline, self).__init__(**kwargs)

    def on_parent(self, instance, value):
        bind = self.bind
        unbind = self.unbind
        if self.parent:
            bind(text_color=self.markup_text)
            bind(text_color_highlight=self.markup_text)
            bind(snippets=self.markup_text)
            bind(highlight_spans=self.draw_spans)
            bind(size=self.compute_snippet_layout)
            bind(pos=self.compute_snippet_layout)
        # else:
        #     funbind("text_color", self.markup_text)
        #     funbind("text_color_highlight", self.markup_text)
        #     funbind("snippets", self.markup_text)
        #
        #     funbind("highlight_spans", self.draw_spans)
        #     funbind('size', self.compute_snippet_layout)
        #     funbind('pos', self.compute_snippet_layout)

    def add_snippet(self, snippet: TextSnippet):
        self.snippets.append(snippet)

    def on_bg_color(self, instance, value):
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
                    f"[font={self.font_family_mono}][color={self.text_color_highlight}]{snippet.text}[/color][/font]"
                )
            else:
                texts.append(f"[color={self.text_color}]{snippet.text}[/color]")

        self.text = " ".join(texts)
        return True

    @classmethod
    def tokenize_text(cls, s: str) -> Iterator[str]:
        tokens = s.split()
        last_token = len(tokens) - 1
        for i, token in enumerate(tokens):
            yield token
            if i < last_token:
                yield " "

    def iter_tokens(self) -> Iterator[tuple[str, bool]]:
        """
        For each snippet in self.text_snippets, tokenize the text (including white_space) and yield tuples of token,
         is_highlight

        """
        for snippet in self.snippets:
            hl = snippet.highlight
            tokens = self.tokenize_text(snippet.text)
            for token in tokens:
                yield token, hl

    def draw_spans(self, instance, value):
        """Draw highlighting"""

        # def clear_canvas(dt):
        #     with self.canvas.before:
        #         self.canvas.before.clear()

        def draw_rects(dt):
            with self.canvas.before:
                self.canvas.before.clear()
            if self.highlight_spans:
                with self.canvas.before:
                    Color(*self.highlight_color)
                    for span in self.highlight_spans:
                        RoundedRectangle(
                            pos=(span.pos_x, span.pos_y),
                            size=(span.w, span.h),
                            radius=(3,),
                        )

        sch_cb(0, draw_rects)

    def compute_snippet_layout(self, instance, value):
        """
        Compute extents of each of our snippets
        Notes
        ------
        This assumes our text_size is self.width, None. The result is a label that is constrained horizontally
        but can grow vertically.
        """
        if not self.width:
            self.highlight_spans = []
            return
        l = self._label
        space_width, _ = l.get_cached_extents()(" ")
        l_opts = {
            **l.options,
            **{"font_name": self.font_family_normal, "space_width": space_width},
        }
        l_opts_hl = {
            **l.options,
            **{"font_name": self.font_family_mono, "space_width": space_width},
        }
        current_w, current_h = 0, 0
        lines = []
        max_w = self.width

        max_h = None

        for token, hl in self.iter_tokens():
            current_w, current_h, clipped = layout_text(
                token,
                lines,
                (current_w, current_h),
                (max_w, max_h),
                l_opts if not hl else l_opts_hl,
                l.get_cached_extents(),
                True,
                False,
            )

        # Signal that this is the end of the text
        current_w, current_h, clipped = layout_text(
            "",
            lines,
            (current_w, current_h),
            (max_w, max_h),
            l_opts,
            l.get_cached_extents(),
            True,
            True,
        )

        # We do this at the token level as snippets can cross lines
        # Keep a generator with tokens, is_highlight
        i_tokens = self.iter_tokens()

        # Each line goes from top (self.height) to bottom
        # line_y tracks the offset from self.height
        # y will change with each line

        hl_spans = []
        current_span: Optional[HighlightSpan] = None
        line_y_offset = 0

        for i, line in enumerate(lines):
            line_y_offset += line.h
            # Compute the absolute y
            line_pos_y = self.y + self.height - line_y_offset
            # Absolute x - this shouldn't change?
            line_pos_x = self.x + self.padding_x

            # Keep track of the current x offset which changes with each token
            token_rel_x = 0
            last_word = len(line.words) - 1
            for word_idx, word in enumerate(line.words):
                word_width = word.lw
                if not word.text:
                    continue
                try:
                    _, is_highlight = next(i_tokens)
                except StopIteration:
                    Logger.debug("Ran out of tokens")
                    self.highlight_spans = []
                    break
                token_abs_x = dp(token_rel_x) + dp(line_pos_x)
                token_abs_y = dp(line_pos_y)
                if is_highlight:
                    if current_span is None:
                        # Start a new span
                        current_span = HighlightSpan(
                            pos_x=dp(token_abs_x) + dp(space_width / 2),
                            pos_y=dp(token_abs_y),
                            w=dp(word_width + space_width * 4),
                            h=dp(line.h),
                        )
                        token_rel_x += word_width
                    else:
                        # Extend span
                        current_span = HighlightSpan(
                            pos_x=current_span.pos_x,
                            pos_y=current_span.pos_y,
                            w=current_span.w + word_width,
                            h=current_span.h,
                        )
                        token_rel_x += word_width
                else:
                    if current_span is None:
                        # We don't need to close a span
                        token_rel_x += word_width
                    else:
                        # This token ends the highlighting
                        hl_spans.append(current_span)
                        current_span = None
                        token_rel_x += word_width
                if word_idx == last_word and current_span is not None:
                    # Ensure we've closed out spans
                    current_span = HighlightSpan(
                        pos_x=dp(token_abs_x),
                        pos_y=dp(token_abs_y),
                        w=current_span.w + word_width,
                        h=dp(line.h),
                    )
                    hl_spans.append(current_span)
                    current_span = None

        self.highlight_spans = hl_spans
