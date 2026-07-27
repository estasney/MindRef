"""Hand-written stub for `kivy.uix.codeinput` (kivy 2.3.1).

`lexer` is never None in practice: `__init__` unconditionally assigns a
`PythonLexer` before user kwargs apply. `style` accepts what pygments'
`get_style_by_name` returns — a `Style` subclass, not an instance.
"""

from pygments.formatters.bbcode import BBCodeFormatter
from pygments.lexer import Lexer
from pygments.style import Style

from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.behaviors import CodeNavigationBehavior
from kivy.uix.textinput import TextInput

__all__ = ("CodeInput",)

class CodeInput(CodeNavigationBehavior, TextInput):
    lexer: ObjectProperty[Lexer]
    style_name: OptionProperty[str]
    style: ObjectProperty[type[Style] | None]
    formatter: BBCodeFormatter[str]
    text_color: str
    use_text_color: bool
    def __init__(self, **kwargs: object) -> None: ...
    def on_style_name(self, *args: object) -> None: ...
    def on_style(self, *args: object) -> None: ...
    def on_lexer(self, instance: object, value: Lexer) -> None: ...
    def on_foreground_color(self, instance: object, text_color: object) -> None: ...
