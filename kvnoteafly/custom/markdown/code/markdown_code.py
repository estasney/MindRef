from kivy.properties import ObjectProperty, OptionProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from pygments import lexers, styles, highlight
from pygments.formatters.bbcode import BBCodeFormatter

from utils import import_kv

import_kv(__file__)


class MarkdownCode(GridLayout):
    text_content = StringProperty()
    code_content = StringProperty()
    content = ObjectProperty()
    lexer = ObjectProperty(None)
    background_color = StringProperty()

    def __init__(self, lexer, **kwargs):
        super(MarkdownCode, self).__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.formatter = BBCodeFormatter(style=self.styler)
        self.lexer = lexers.get_lexer_by_name(lexer)
        self.background_color = self.styler.background_color

    def on_text_content(self, instance, value):
        ntext = highlight(self.text_content, self.lexer, self.formatter)
        # ntext = ntext.replace(u'\x01', u'&bl;').replace(u'\x02', u'&br;')
        # # replace special chars with &bl; and &br;
        # # ntext = ''.join((u'[color=', 'white', u']',
        #
        # #                  ntext, u'[/color]'))
        # ntext = '\n'.join(ntext)
        # # ntext = ntext.replace(u'\n', u'')
        # # remove possible extra highlight options
        # ntext = ntext.replace(u'[u]', '').replace(u'[/u]', '')
        self.code_content = ntext
