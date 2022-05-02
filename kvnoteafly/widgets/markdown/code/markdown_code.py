from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments import lexers, styles
from pygments.formatters.bbcode import BBCodeFormatter
from pygments.lexers import PythonLexer

from utils import import_kv

import_kv(__file__)


class MarkdownCode(GridLayout):
    text_content = StringProperty()
    content = ObjectProperty()
    lexer = ObjectProperty(PythonLexer())
    background_color = StringProperty()

    def __init__(self, lexer, **kwargs):
        super(MarkdownCode, self).__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.formatter = BBCodeFormatter(style=self.styler)
        self.lexer = lexers.get_lexer_by_name(lexer)
        self.background_color = self.styler.background_color
