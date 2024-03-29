from kivy.properties import StringProperty, ListProperty
from kivy.uix.gridlayout import GridLayout

from lib.domain.md_parser_types import MdBlockQuote
from lib.utils import import_kv
from lib.widgets.markdown.markdown_parsing_mixin import MarkdownLabelParsingMixin

import_kv(__file__)


class MarkdownBlockQuote(GridLayout, MarkdownLabelParsingMixin):
    snippets = ListProperty()
    open_bbcode_tag = StringProperty()

    def __init__(self, **kwargs):
        super(MarkdownBlockQuote, self).__init__(**kwargs)

    def visit(self, node: MdBlockQuote):
        for node in node["children"]:
            super().visit(node)
