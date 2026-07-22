from kivy.core.text import Label as CoreLabel
from kivy.input.motionevent import MotionEvent
from kivy.logger import Logger
from kivy.properties import AliasProperty, ObjectProperty, StringProperty
from kivy.uix.codeinput import CodeInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from pygments import lexers
from pygments.lexers import PythonLexer
from pygments.util import ClassNotFound

from mindref.lib.utils import import_kv
from mindref.lib.widgets.markdown.code.jetbrains_dark import JetBrainsDark

import_kv(__file__)


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
    content = ObjectProperty()
    lexer = ObjectProperty(PythonLexer())
    background_color = StringProperty()
    lexer_name = StringProperty()

    def _get_text_content(self):
        return self._text_content

    def _set_text_content(self, value):
        self._text_content = value.strip()

    text_content = AliasProperty(
        _get_text_content, _set_text_content, bind=["_text_content"]
    )

    def __init__(self, lexer: str | None, **kwargs) -> None:
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
            Logger.warn(f"Unknown lexer {self.lexer_name} - falling back to markdown")
            self.lexer = lexers.get_lexer_by_name("markdown")
        self.background_color = self.styler.background_color
