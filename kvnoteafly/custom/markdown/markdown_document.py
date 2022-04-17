from functools import partial

import marko
from kivy.properties import (
    AliasProperty,
    DictProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex, get_hex_from_color
from marko.ext.gfm import gfm

from custom.markdown.code.markdown_code import MarkdownCode
from custom.markdown.list.markdown_list import MarkdownList
from custom.markdown.list.markdown_list_item import MarkdownListItem
from custom.markdown.markdown_heading import MarkdownHeading
from custom.markdown.table.markdown_table import (
    MarkdownCell,
    MarkdownCellContent,
    MarkdownTable,
)
from utils import import_kv

import_kv(__file__)


class MarkdownDocument(ScrollView):
    text = StringProperty(None)
    base_font_size = NumericProperty(31)

    def _get_bgc(self):
        return get_color_from_hex(self.colors.background)

    def _set_bgc(self, value):
        self.colors.background = get_hex_from_color(value)[1:]

    background_color = AliasProperty(_get_bgc, _set_bgc, bind=("colors",), cache=True)

    colors = DictProperty(
        {
            "background": "37474fff",
            "code": "2b2b2bff",
            "link": "ce5c00ff",
            "paragraph": "202020ff",
            "title": "204a87ff",
            "bullet": "000000ff",
        }
    )
    underline_color = StringProperty("000000ff")
    content = ObjectProperty(None)

    def __init__(self, content_data: dict, **kwargs):
        super(MarkdownDocument, self).__init__(**kwargs)
        self._parser = gfm
        self.text = content_data["text"]
        self.current = None
        self.current_params = None
        self.do_scroll_x = False
        self.do_scroll_y = True

    def on_text(self, instance, value):
        self._load_from_text()

    def render(self):
        self._load_from_text()

    @classmethod
    def get_node_text(cls, node):
        if isinstance(node.children, str):
            return node.children
        if len(node.children) > 1:
            return " ".join([cls.get_node_text(c) for c in node.children])

        return cls.get_node_text(node.children[0])

    def _load_list_node(self, node: "marko.block.List"):
        list_widget = MarkdownList()
        self.content.add_widget(list_widget)
        self.current = list_widget
        for child in node.children:
            self._load_list_item(child, node.start)
        self.current = self.content

    def _load_list_item(self, node: "marko.block.ListItem", level: int):

        list_item = MarkdownListItem(text=self.get_node_text(node), level=level)
        self.current.add_widget(list_item)

    def _load_code_node(self, node: "marko.block.FencedCode"):
        item = MarkdownCode(lexer=node.lang)
        item.text_content = self.get_node_text(node)
        self.current.add_widget(item)

    def _load_table(self, node: "marko.ext.gfm.elements.Table"):
        n_cols = max((len(row.children) for row in node.children))
        table = MarkdownTable(cols=n_cols)
        self.current.add_widget(table)
        self.current = table

        def _format_cell_text(text, bold: bool):
            if bold:
                return f"[b]{text}[/b]"
            else:
                return text

        apply_bold = partial(_format_cell_text, bold=True)
        noop_text = lambda x: x

        for row_idx, row in enumerate(node.children):
            f_text = apply_bold if row_idx == 0 else noop_text
            for cell in row.children:
                try:
                    cell_text = self.get_node_text(cell)
                    cell_text = " " if not cell_text else cell_text
                except IndexError:
                    cell_text = " "
                cell_text = f_text(cell_text)
                cell_widget = MarkdownCell()
                cell_label = MarkdownCellContent(text=cell_text, document=self)
                cell_widget.add_widget(cell_label)
                self.current.add_widget(cell_widget)
        self.current = self.content

    def _load_node(self, node: "marko.block"):
        cls = node.__class__
        if cls is marko.block.Heading:
            label = MarkdownHeading(
                document=self,
                level=node.level,
                content=node.children[0].children,
            )
            self.content.add_widget(label)

        elif cls is marko.block.List:
            self._load_list_node(node)

        elif cls is marko.block.FencedCode:
            self._load_code_node(node)

        elif cls is marko.ext.gfm.elements.Table:
            self._load_table(node)

    def _load_from_text(self, *args):
        self.content.clear_widgets()
        document = self._parser.parse(self.text)
        for child in document.children:
            self._load_node(child)
