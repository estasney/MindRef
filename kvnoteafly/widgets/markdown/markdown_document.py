from functools import partial
from operator import concat
from typing import Union
from kivy.logger import Logger
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
from toolz import concatv

from widgets.markdown.code.code_span import MarkdownCodeSpan
from widgets.markdown.code.markdown_code import MarkdownCode
from widgets.markdown.list.markdown_list import MarkdownList
from widgets.markdown.list.markdown_list_item import MarkdownListItem
from widgets.markdown.markdown_heading import MarkdownHeading
from widgets.markdown.paragraph.markdown_paragraph import MarkdownParagraph
from widgets.markdown.table.markdown_table import (
    MarkdownCell,
    MarkdownCellContent,
    MarkdownRow,
    MarkdownTable,
)
from services.backend.utils import get_md_node_text
from utils import import_kv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.domain.md_parser_types import *

import_kv(__file__)


class MarkdownDocument(ScrollView):
    text = StringProperty(None)
    title = StringProperty(None)
    document = ObjectProperty()
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
        self.document = content_data["document"]
        self.text = content_data["text"]
        self.title = content_data["title"]
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
        return get_md_node_text(node)

    def _load_paragraph_node(self, node: "Union[MdBlockText, MdParagraph]"):
        Logger.debug(f"Paragraph Node : {node}")
        if not node["children"]:
            return
        for child in node["children"]:
            self._load_node(child)

    def _load_list_node(self, node: "Union[MdListOrdered, MdListUnordered]"):
        list_widget = MarkdownList()
        self.content.add_widget(list_widget)
        self.current = list_widget
        for child in node["children"]:
            self._load_list_item(child, node["level"])
        self.current = self.content

    def _load_list_item(self, node: "Union[MdListItem]", level: int):
        list_item = MarkdownListItem(text=self.get_node_text(node), level=level)
        self.current.add_widget(list_item)

    def _load_block_code_node(self, node: "MdBlockCode"):
        item = MarkdownCode(lexer=node["info"])
        item.text_content = self.get_node_text(node)
        self.content.add_widget(item)

    def _load_code_span_node(self, node: "MdCodeSpan"):
        item = MarkdownCodeSpan(text=node["text"])

        if self.current:
            self.current.add_widget(item)
        else:
            self.content.add_widget(item)

    def _load_heading(self, node: "MdHeading"):
        node: "MdHeading"
        if not node["children"]:
            return
        label_text = node["children"][0]["text"]
        if label_text == self.title:
            return
        label = MarkdownHeading(
            document=self,
            level=node["level"],
            content=label_text,
        )
        self.content.add_widget(label)

    def _load_table(self, node: "MdTable"):
        table_head = node["children"][0]
        n_cols = len(table_head["children"])
        table = MarkdownTable(cols=1)
        self.content.add_widget(table)
        self.current = table

        # Table head row
        head_row = MarkdownRow(is_head=True)
        for cell in table_head["children"]:
            cell_widget = MarkdownCell(align=cell.get("align"))
            cell_label = MarkdownCellContent(
                text=self.get_node_text(cell), document=self
            )
            cell_widget.add_widget(cell_label)
            head_row.add_widget(cell_widget)
        self.current.add_widget(head_row)

        rows = node["children"][1]["children"]
        for row_idx, row in enumerate(rows):
            row_widget = MarkdownRow(is_head=False)
            self.current.add_widget(row_widget)
            for cell in row["children"]:
                cell_text = self.get_node_text(cell)
                cell_widget = MarkdownCell(align=cell.get("align"))
                cell_label = MarkdownCellContent(text=cell_text, document=self)
                cell_widget.add_widget(cell_label)
                row_widget.add_widget(cell_widget)

        self.current = self.content

    def _load_node(self, node: "MD_TYPES"):
        routes = {
            "heading": self._load_heading,
            "list": self._load_list_node,
            "block_code": self._load_block_code_node,
            "codespan": self._load_code_span_node,
            "table": self._load_table,
            "block_text": self._load_paragraph_node,
            "paragraph": self._load_paragraph_node,
        }

        node_type: "MD_LIT_TYPES" = node["type"]
        func = routes.get(node_type, None)
        if func:
            Logger.debug(f"Loading {node_type} with {func!r}")
            # noinspection PyArgumentList
            func(node)
        else:
            Logger.info(f"Skipping Node Type {node_type}")

    def _load_from_text(self, *args):
        """Main entry point for loading"""
        self.content.clear_widgets()
        self.current = None
        for child in self.document:
            self._load_node(child)
