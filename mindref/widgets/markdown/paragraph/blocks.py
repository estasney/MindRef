from kivy.properties import StringProperty, ListProperty
from kivy.uix.gridlayout import GridLayout

from utils import import_kv
from widgets.markdown.markdown_parsing_mixin import MarkdownLabelParsingMixin

import_kv(__file__)


class MarkdownBlockQuote(GridLayout, MarkdownLabelParsingMixin):
    snippets = ListProperty()
    open_bbcode_tag = StringProperty()

    def __init__(self, **kwargs):
        super(MarkdownBlockQuote, self).__init__(**kwargs)
