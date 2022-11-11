from typing import Optional

from kivy import Logger
from kivy.properties import AliasProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments import lexers, styles
from pygments.formatters.bbcode import BBCodeFormatter
from pygments.lexers import PythonLexer
from pygments.util import ClassNotFound

from utils import import_kv

import_kv(__file__)


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

    def __init__(self, lexer: Optional[str], **kwargs):
        super(MarkdownCode, self).__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.formatter = BBCodeFormatter(style=self.styler)
        self.lexer_name = lexer.strip() if lexer else "markdown"
        try:
            self.lexer = (
                lexers.get_lexer_by_name(self.lexer_name)
                if lexer
                else lexers.get_lexer_by_name("markdown")
            )
        except ClassNotFound as e:
            Logger.warn(f"Unknown lexer {self.lexer_name} - falling back to markdown")
            self.lexer = lexers.get_lexer_by_name("markdown")
        self.background_color = self.styler.background_color
