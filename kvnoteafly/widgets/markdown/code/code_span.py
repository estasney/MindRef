from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments import lexers, styles
from pygments.formatters.bbcode import BBCodeFormatter

from io import StringIO

from pygments.token import Token

from utils import import_kv

import_kv(__file__)


class MarkdownCodeSpan(GridLayout):
    content = ObjectProperty()
    text = StringProperty()
    text_content = StringProperty()
    background_color = StringProperty()

    def __init__(self, text, **kwargs):
        super(MarkdownCodeSpan, self).__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.text = text
        self.background_color = self.styler.background_color

    def on_text(self, previous, new):
        # Wrap in BBCode
        bb_text = f"[color={self.styler.styles[Token.Text]}]{new}[/color]"
        self.text_content = bb_text
