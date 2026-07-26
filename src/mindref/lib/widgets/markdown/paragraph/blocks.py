from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from mindref.lib.domain.md_parser_types import MdBlockQuote
from mindref.lib.widgets.markdown.markdown_parsing_mixin import (
    MarkdownLabelParsingMixin,
)

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import LabelHighlightInline mindref.lib.widgets.behavior
<MarkdownBlockQuote>:
    cols: 1
    size_hint_y: None
    height: content.texture_size[1] + dp(20)
    id: parent
    padding: dp(10), dp(10), 0, dp(10)
    canvas:
        Color:
            rgba: (*app.colors['Gray-200'][:3], 0.5)
        Rectangle:
            pos: [self.pos[0], self.pos[1] + dp(5)]
            size: [self.size[0], self.size[1] -dp(10)]
        Color:
            rgba: app.colors['Accent-One']
        Rectangle:
            pos: [self.pos[0], self.pos[1] + dp(5)]
            size: [sp(4), self.height - dp(10)]
    LabelHighlightInline:
        id: content
        snippets: root.snippets
        bg_color: app.colors['Gray-500']
        highlight_color: app.colors['Codespan']
        text_threshold: 170
        valign: 'center'
        size: self.texture_size
        text_size: self.width, None


""")


class MarkdownBlockQuote(GridLayout, MarkdownLabelParsingMixin):
    snippets = ListProperty()
    open_bbcode_tag = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def visit(self, node: MdBlockQuote):
        for child_node in node["children"]:
            super().visit(child_node)
