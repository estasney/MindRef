from __future__ import annotations

from kivy.core.text import Label as CoreLabel
from kivy.input.motionevent import MotionEvent
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import AliasProperty, ObjectProperty, StringProperty
from kivy.uix.codeinput import CodeInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from pygments import lexers
from pygments.lexer import Lexer
from pygments.lexers import PythonLexer
from pygments.util import ClassNotFound

from mindref.lib.widgets.markdown.code.jetbrains_dark import JetBrainsDark

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import platform kivy.utils.platform
#:import JetBrainsDark mindref.lib.widgets.markdown.code.jetbrains_dark.JetBrainsDark
<MarkdownCode>:
    cols: 1
    content: content
    size_hint_y: None
    height: content.minimum_height
    canvas:
        Color:
            rgb: parse_color(root.background_color)
        Rectangle:
            pos: self.x - 1, self.y - 1
            size: self.width + 2, self.height + 2
        Color:
            rgb: parse_color(root.background_color)
        Rectangle:
            pos: self.pos
            size: self.size
    HorizontalWheelScrollView:
        id: scroller
        size_hint_y: None
        height: content.minimum_height
        do_scroll_x: True
        do_scroll_y: False
        effect_cls: "ScrollEffect"
        bar_width: dp(4)
        scroll_type: ["bars", "content"]
        NoWrapCodeInput:
            id: content
            background_normal: ""
            background_active: ""
            background_color: parse_color(root.background_color)
            size_hint: None, None
            width: max(scroller.width, self.minimum_width)
            height: self.minimum_height
            do_wrap: False
            text: root.text_content
            readonly: True
            style: JetBrainsDark
            lexer: root.lexer
            font_name: "JetBrainsMono"
            mipmap: True
            font_size: sp(app.base_font_size - 4)
            cursor_color: 0, 0, 0, 0
            is_focusable: True
            keyboard_mode: "managed" if platform == "android" else "auto"
""")


class HorizontalWheelScrollView(ScrollView):
    """ScrollView that declines vertical mouse wheel events and mouse drags.

    ScrollView consumes wheel events even on axes it cannot scroll, which
    blocks the enclosing document's vertical scroll while the cursor is
    over this widget. Declining them lets the parent handle the event.

    ScrollView also holds every touch to test for a scroll gesture, which
    keeps mouse drags from reaching the code widget as text selection.
    Mouse drags go straight to the child; horizontal scrolling stays
    available through the wheel and the scrollbar. Finger touches keep the
    scroll-first behavior.
    """

    def on_scroll_start(
        self, touch: MotionEvent, check_children: bool = True
    ) -> bool | None:
        if "button" in touch.profile and touch.button in ("scrollup", "scrolldown"):
            return False
        return super().on_scroll_start(touch, check_children)

    def on_touch_down(self, touch: MotionEvent) -> bool | None:
        if (
            self.collide_point(*touch.pos)
            and "button" in touch.profile
            and not touch.button.startswith("scroll")
            and not self.touch_in_horizontal_bar(touch)
        ):
            return self.simulate_touch_down(touch)
        return super().on_touch_down(touch)

    def touch_in_horizontal_bar(self, touch: MotionEvent) -> bool:
        if "bars" not in self.scroll_type or self.hbar[1] >= 1.0:
            return False
        distance = (
            touch.y - self.y - self.bar_margin
            if self.bar_pos_x == "bottom"
            else self.top - touch.y - self.bar_margin
        )
        return 0 <= distance <= self.bar_width


class NoWrapCodeInput(CodeInput):
    """CodeInput that reports the width of its widest line as ``minimum_width``.

    TextInput exposes no minimum_width, so a horizontal ScrollView has nothing
    to size against; this measures it with the widget's own font settings.
    Pair with ``do_wrap: False``.
    """

    def long_touch(self, dt: float) -> None:
        """Select the word under a long press.

        The base implementation shows the paste bubble, which has no use
        in a readonly widget.
        """
        self.cancel_long_touch_event()
        if self.use_handles and not self.selection_text:
            self.dispatch("on_double_tap")

    def get_minimum_width(self) -> float:
        label = CoreLabel(font_name=self.font_name, font_size=self.font_size)
        line_widths = (
            label.get_extents(line.replace("\t", " " * self.tab_width))[0]
            for line in self.text.splitlines()
        )
        return max(line_widths, default=0) + self.padding[0] + self.padding[2]

    minimum_width = AliasProperty(
        get_minimum_width,
        bind=("text", "font_name", "font_size", "tab_width", "padding"),
        cache=True,
    )


class MarkdownCode(GridLayout):
    _text_content = StringProperty()
    content: ObjectProperty[NoWrapCodeInput] = ObjectProperty()
    lexer: ObjectProperty[Lexer] = ObjectProperty(PythonLexer())
    background_color = StringProperty()
    lexer_name = StringProperty()

    def _get_text_content(self) -> str:
        return self._text_content

    def _set_text_content(self, value: str) -> None:
        self._text_content = value.strip()

    text_content: AliasProperty[str] = AliasProperty(
        _get_text_content, _set_text_content, bind=["_text_content"]
    )

    def __init__(self, lexer: str | None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.styler = JetBrainsDark
        self.lexer_name = lexer.strip() if lexer else "markdown"
        try:
            self.lexer = (
                lexers.get_lexer_by_name(self.lexer_name)
                if lexer
                else lexers.get_lexer_by_name("markdown")
            )
        except ClassNotFound:
            Logger.warning(
                f"Unknown lexer {self.lexer_name} - falling back to markdown"
            )
            self.lexer = lexers.get_lexer_by_name("markdown")
        self.background_color = self.styler.background_color
