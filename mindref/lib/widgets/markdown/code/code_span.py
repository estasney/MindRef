from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments import styles
from pygments.token import Token

from lib.utils import import_kv

import_kv(__file__)


class MarkdownCodeSpan(GridLayout):
    content = ObjectProperty()
    raw_text = StringProperty()
    text = StringProperty()
    background_color = StringProperty()

    def __init__(self, text, **kwargs):
        super(MarkdownCodeSpan, self).__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.background_color = self.styler.background_color
        self.raw_text = text

    def on_raw_text(self, _, new):
        # Wrap in BBCode
        bb_text = f"[color={self.styler.styles[Token.Text]}]{new}[/color]"
        self.text = bb_text
