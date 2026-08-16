from __future__ import annotations

from functools import lru_cache
from typing import Literal, NamedTuple

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.label import Label
from kivy.utils import escape_markup

from mindref.lib.ext import (
    compute_ref_coords,
    compute_text_contrast,
)

Builder.load_string("""
<LabelHighlightInline>:
    mipmap: True
    width: self.texture_size[0]
    height: self.texture_size[1]
    text_size: self.width, None
    font_size: sp(app.base_font_size)
    font_name: app.fonts['mono']
    markup: True
    font_family_normal: app.fonts['mono']
    font_family_mono: app.fonts['mono']
    highlight_padding: (self.font_size * 0.19, 0)
    highlight_radius: [self.font_size * 0.06]
    kbd_color: app.colors['Keyboard']
    kbd_shadow_color: app.colors['KeyboardShadow']
""")


class TextSnippet(NamedTuple):
    text: str
    highlight_tag: Literal["hl", "kbd"] | None


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
    highlight_radius: VariableListProperty
        List of 1-4 radii for the highlighted text ref's highlight rectangle
    """

    bg_color = ColorProperty()
    highlight_color = ColorProperty()
    kbd_color = ColorProperty()
    kbd_shadow_color = ColorProperty()
    text_color = StringProperty("#ffffff")
    text_color_highlight = StringProperty("#ffffff")
    font_family_normal = StringProperty()
    font_family_mono = StringProperty()
    snippets: ListProperty[TextSnippet] = ListProperty()
    has_parent = BooleanProperty(defaultvalue=False)
    highlight_padding_x = NumericProperty(defaultvalue=0)
    highlight_padding_y = NumericProperty(defaultvalue=0)
    highlight_padding = ReferenceListProperty(highlight_padding_x, highlight_padding_y)
    highlight_radius = VariableListProperty([1])

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.markup_text_trigger = Clock.create_trigger(self.markup_text)
        self.handle_contrast_trigger = Clock.create_trigger(self.handle_contrast)
        self.draw_ref_spans_trigger = Clock.create_trigger(self.draw_ref_spans)

    def on_parent(self, *_args: object) -> None:
        fbind = self.fbind
        funbind = self.funbind
        if self.parent:
            fbind("text_color", self.markup_text_trigger)
            fbind("text_color_highlight", self.markup_text_trigger)
            fbind("bg_color", self.handle_contrast_trigger)
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
            funbind("snippets", self.markup_text_trigger)
            funbind("refs", self.draw_ref_spans_trigger)
            funbind("size", self.draw_ref_spans_trigger)
            funbind("pos", self.draw_ref_spans_trigger)
            funbind("padding_x", self.draw_ref_spans_trigger)
            funbind("padding_y", self.draw_ref_spans_trigger)

    def add_snippet(self, snippet: TextSnippet) -> None:
        self.snippets.append(snippet)

    def handle_contrast(self, *_args: object) -> bool:
        """Update computed text_colors"""
        self.text_color = get_cached_text_contrast(
            background_color=tuple(self.bg_color),
            highlight_color=None,
        )
        self.text_color_highlight = get_cached_text_contrast(
            background_color=tuple(self.bg_color),
            highlight_color=tuple(self.highlight_color),
        )
        return True

    def markup_text(self, *_args: object, **_kwargs: object) -> bool:
        """Update the markup within text to reflect new colors"""
        texts: list[str] = []
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
                texts.append(f"[color={self.text_color}]{snippet_text}[/color]")

        # Snippets preserve leading/trailing whitespace
        self.text = "".join(texts)
        return True

    def compute_ref_coords(
        self, span: tuple[float, float, float, float]
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
        return compute_ref_coords(
            self.width,
            self.height,
            self.x,
            self.y,
            self.texture_size[0],
            self.texture_size[1],
            span[0],
            span[1],
            span[2],
            span[3],
            self.highlight_padding_x,
            self.highlight_padding_y,
        )

    def draw_ref_spans(self, *_args: object, **_kwargs: object) -> None:
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
                RoundedRectangle(
                    pos=(x1, y1), size=(w, h), radius=self.highlight_radius
                )

            kbd_inset_x = self.font_size * 0.11
            kbd_inset_y = self.font_size * 0.11
            for span in self.refs.get("kbd", []):
                x1, y1, x2, y2 = self.compute_ref_coords(span)
                w = x2 - x1
                h = y2 - y1
                # darker background
                Color(*self.kbd_shadow_color)
                RoundedRectangle(
                    pos=(x1 - kbd_inset_x, y1 - kbd_inset_y),
                    size=(w, h),
                    radius=self.highlight_radius,
                )
                Color(*self.kbd_color)
                RoundedRectangle(
                    pos=(x1, y1), size=(w, h), radius=self.highlight_radius
                )


@lru_cache(maxsize=128)
def get_cached_text_contrast(
    *,
    background_color: tuple[float, float, float, float],
    highlight_color: tuple[float, float, float, float] | None = None,
) -> str:
    """
    Set text as white or black depending on bg
    """
    return compute_text_contrast(background_color, highlight_color)
