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
            use_bubble: False
            use_handles: False
            font_name: "JetBrainsMono"
            mipmap: True
            font_size: sp(app.base_font_size - 4)
            cursor_color: 0, 0, 0, 0
            is_focusable: False
            keyboard_mode: "managed"
""")


class HorizontalWheelScrollView(ScrollView):
    """ScrollView that declines vertical mouse wheel events.

    ScrollView consumes wheel events even on axes it cannot scroll, which
    blocks the enclosing document's vertical scroll while the cursor is
    over this widget. Declining them lets the parent handle the event.
    """

    def on_scroll_start(
        self, touch: MotionEvent, check_children: bool = True
    ) -> bool | None:
        if "button" in touch.profile and touch.button in ("scrollup", "scrolldown"):
            return False
        return super().on_scroll_start(touch, check_children)


class NoWrapCodeInput(CodeInput):
    """CodeInput that reports the width of its widest line as ``minimum_width``.

    TextInput exposes no minimum_width, so a horizontal ScrollView has nothing
    to size against; this measures it with the widget's own font settings.
    Pair with ``do_wrap: False``.
    """

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
