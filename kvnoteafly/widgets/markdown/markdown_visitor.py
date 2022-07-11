from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Union, overload

from kivy import Logger
from kivy.uix.label import Label

from domain.parser import get_md_node_text
from widgets.markdown.code.code_span import MarkdownCodeSpan
from widgets.markdown.code.markdown_code import MarkdownCode
from widgets.markdown.list.markdown_list import MarkdownList
from widgets.markdown.list.markdown_list_item import MarkdownListItem
from widgets.markdown.markdown_block import MarkdownBlock, MarkdownHeading
from widgets.markdown.markdown_interceptor import WidgetIntercept
from widgets.markdown.paragraph.blocks import MarkdownBlockQuote
from widgets.markdown.table.markdown_table import (
    MarkdownCellLabel,
    MarkdownRow,
    MarkdownTable,
)
from kivy.uix.layout import Layout

if TYPE_CHECKING:
    from domain.md_parser_types import *
    from kivy.uix.widget import Widget


class MarkdownVisitor:
    text: str
    title: str

    blocks: set["MD_LIT_BLOCK_TYPES"] = {
        "newline",
        "thematic_break",
        "heading",
        "block_code",
        "block_quote",
        "block_text",
        "list",
        "paragraph" "list_item",
    }
    inline: set["MD_LIT_INLINE_TYPES"] = {"codespan", "strong", "text"}

    def __init__(self, *args, **kwargs):
        self.current_list = deque([])
        self.bb_directives = deque([])
        self.visiting_table = False
        self.tip_type_layout = False
        self.has_intercept = False
        self.debug_nodes = kwargs.get("debug_nodes", False)

    @overload
    def push(self, widget: Widget):
        ...

    @overload
    def push(self, widget: Layout):
        ...

    @overload
    def push(self, widget: "MD_INLINE_TYPES"):
        ...

    def push(self, widget):
        if isinstance(widget, dict):
            raise AttributeError(
                f"Passing {widget} to push is only supported with WidgetIntercept"
            )
        if len(self.current_list):
            self.current_list[-1].add_widget(widget)
            if isinstance(widget, Layout):
                self.current_list.append(widget)
                Logger.debug(
                    f"Pushed-->: {widget.__class__.__name__} --> {self.current_list[-1].__class__.__name__}"
                )
            else:
                self.debug_nodes and Logger.debug(
                    f"Pushed-->: {widget.__class__.__name__} --> {self.current_list[-1].__class__.__name__} XXX"
                )
        else:
            self.debug_nodes and Logger.debug(
                f"New Stack with {widget.__class__.__name__}"
            )
            self.current_list.append(widget)

    def pop(self):
        popped = self.current_list.pop()
        self.debug_nodes and Logger.debug(
            f"<--  Popped : {popped.__class__.__name__}  <-- {self.current_list[-1].__class__.__name__ if self.current_list else 'Empty'}"
        )
        return popped

    def pop_entry(self):
        popped = self.current_list.popleft()
        self.current_list.clear()
        self.debug_nodes and Logger.debug(
            f"<--  Popped Entry : {popped.__class__.__name__}"
        )
        return popped

    def visit(self, node: "MD_TYPES", **kwargs):
        node_type: Optional["MD_LIT_TYPES"] = node.get("type", "generic")
        visit_func = getattr(self, f"visit_{node_type}")
        return visit_func(node, **kwargs)

    def visit_heading(self, node: "MdHeading", **kwargs) -> bool:
        heading_widget = MarkdownHeading()
        heading_widget.level = node["level"]
        with WidgetIntercept(visitor=self, widget=heading_widget):
            for node in node["children"]:
                self.visit(node, **kwargs)
        self.push(heading_widget)
        return True

    def visit_table_cell(self, node: "MdTableHeadCell", **kwargs) -> bool:
        cell_label_kwargs = {k: v for k, v in kwargs.items()}
        cell_align = node["align"] if node["align"] else "center"
        cell_bold = node["is_head"]
        cell_label_kwargs.update({"halign": cell_align, "bold": cell_bold})
        cell_widget = MarkdownCellLabel(**cell_label_kwargs)
        with WidgetIntercept(visitor=self, widget=cell_widget):
            for child in node["children"]:
                self.visit(child, **cell_label_kwargs)
        self.push(cell_widget)
        return False

    def visit_table(self, node: "MdTable", **kwargs) -> bool:
        self.visiting_table = True
        table_head = node["children"][0]
        self.push(MarkdownTable())

        # Table head row
        head_kwargs = {k: v for k, v in kwargs.items()}
        head_kwargs.update({"bold": True, "font_hinting": None, "halign": "center"})
        self.push(MarkdownRow())
        for cell in table_head["children"]:
            if self.visit(cell, **head_kwargs):
                self.pop()
        self.pop()

        self.debug_nodes and Logger.debug("Start Table Body")

        del head_kwargs

        rows = node["children"][1]["children"]
        for row_idx, row in enumerate(rows):
            self.push(MarkdownRow())
            for cell in row["children"]:
                if self.visit(cell, **kwargs):
                    self.pop()
            self.pop()
        self.visiting_table = False
        return True

    def visit_paragraph(self, node: "MdParagraph", **kwargs) -> bool:
        if not node["children"]:
            return False
        paragraph_widget = MarkdownBlock()
        with WidgetIntercept(visitor=self, widget=paragraph_widget):
            for node in node["children"]:
                self.visit(node, **kwargs)
        self.push(paragraph_widget)
        return True

    def visit_list(
        self, node: "Union[MdListOrdered, MdListUnordered]", **kwargs
    ) -> bool:
        self.push(MarkdownList())
        for child in node["children"]:
            if self.visit(child, **kwargs):
                self.pop()
        return True

    def visit_list_item(self, node: "MdListItem", **kwargs) -> bool:
        self.push(
            MarkdownListItem(text=get_md_node_text(node), level=node["level"], **kwargs)
        )
        return True

    def visit_block_code(self, node: "MdBlockCode", **kwargs) -> bool:
        self.push(
            MarkdownCode(
                lexer=node["info"], text_content=get_md_node_text(node), **kwargs
            )
        )
        return True

    def visit_codespan(self, node: "MdCodeSpan", **kwargs) -> bool:
        if self.visiting_table or self.has_intercept:
            self.push(node)

        else:
            self.push(MarkdownCodeSpan(text=node["text"], **kwargs))
        return True

    def visit_text(self, node: "MdText", **kwargs) -> bool:
        if self.has_intercept:
            self.push(node)
            return False
        else:
            para_widget = MarkdownBlock(text=node["text"])
            self.push(para_widget)
            return False

    def visit_block_quote(self, node: "MdBlockQuote", **kwargs) -> bool:
        self.push(MarkdownBlockQuote(text_content=get_md_node_text(node), **kwargs))
        return True

    def visit_newline(self, node: "MdNewLine", **kwargs) -> bool:
        return False

    def visit_strong(self, node: "MdTextStrong", **kwargs):
        for child in node["children"]:
            if self.visit(child, **kwargs):
                self.pop()
        return False

    def visit_emphasis(self, node: "MdTextEmphasis", **kwargs):
        if self.visiting_table or kwargs.get("inline"):
            self.push(node)
            for child in node["children"]:
                self.push(child)
                return True
        else:
            for child in node["children"]:
                if self.visit(child, **kwargs):
                    self.pop()
            return True

    def visit_generic(self, node, **kwargs):
        node_type = node.get("type")
        Logger.info(f"Skipping {node_type if node_type else node} - No Handler")
