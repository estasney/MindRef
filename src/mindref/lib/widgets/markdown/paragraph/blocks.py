from kivy.properties import ListProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from mindref.lib.domain.md_parser_types import MdBlockQuote
from mindref.lib.utils import import_kv
from mindref.lib.widgets.markdown.markdown_parsing_mixin import (
    MarkdownLabelParsingMixin,
)

import_kv(__file__)


class MarkdownBlockQuote(GridLayout, MarkdownLabelParsingMixin):
    snippets = ListProperty()
    open_bbcode_tag = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def visit(self, node: MdBlockQuote):
        for child_node in node["children"]:
            super().visit(child_node)
