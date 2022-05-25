from collections import deque
from typing import TYPE_CHECKING, Union

from kivy import Logger
from kivy.uix.label import Label

from services.backend.utils import get_md_node_text
from widgets.markdown.code.code_span import MarkdownCodeSpan
from widgets.markdown.code.markdown_code import MarkdownCode
from widgets.markdown.list.markdown_list import MarkdownList
from widgets.markdown.list.markdown_list_item import MarkdownListItem
from widgets.markdown.markdown_block import MarkdownBlock, MarkdownHeading
from widgets.markdown.paragraph.blocks import MarkdownBlockQuote
from widgets.markdown.table.markdown_table import (
    MarkdownCellLabel,
    MarkdownRow,
    MarkdownTable,
)

if TYPE_CHECKING:
    from services.domain.md_parser_types import *


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

    def push(self, widget, add: bool = True):
        if len(self.current_list):
            if add:
                self.current_list[-1].add_widget(widget)
                Logger.debug(
                    f"Pushed-->: {widget.__class__.__name__} --> {self.current_list[-1].__class__.__name__}"
                )
            else:
                Logger.debug(
                    f"Pushed-->: {widget.__class__.__name__} XX> {self.current_list[-1].__class__.__name__}"
                )
        else:
            Logger.debug(f"New Stack with {widget.__class__.__name__}")
        self.current_list.append(widget)

    def push_bbcode(self, directive):
        self.bb_directives.append(directive)

    def pop_bbcode(self, text):
        bb_text = text
        while len(self.bb_directives) > 0:
            d_left = self.bb_directives.pop()
            d_right = f"[/{d_left[1:]}"
            bb_text = f"{d_left}{bb_text}{d_right}"
        return bb_text

    def pop(self):
        popped = self.current_list.pop()
        Logger.debug(
            f"<--  Popped : {popped.__class__.__name__}  <-- {self.current_list[-1].__class__.__name__ if self.current_list else 'Empty'}"
        )
        return popped

    def pop_entry(self):
        popped = self.current_list.popleft()
        self.current_list.clear()
        Logger.debug(f"<--  Popped Entry : {popped.__class__.__name__}")
        return popped

    def visit(self, node: "MD_TYPES", **kwargs):
        node_type: Optional["MD_LIT_TYPES"] = node.get("type", "generic")
        visit_func = getattr(self, f"visit_{node_type}")
        return visit_func(node, **kwargs)

    def visit_heading(self, node: "MdHeading", **kwargs) -> bool:
        heading_widget = MarkdownHeading(level=node["level"])
        self.push(heading_widget, add=False)
        for node in node["children"]:
            if self.visit(node):
                self.pop()
        return True

    def visit_table_cell(self, node: "MdTableHeadCell", **kwargs) -> bool:
        # self.push(MarkdownCell())
        cell_label_kwargs = {k: v for k, v in kwargs.items()}
        cell_align = node["align"] if node["align"] else "center"
        cell_bold = node["is_head"]
        cell_label_kwargs.update({"halign": cell_align, "bold": cell_bold})
        for child in node["children"]:
            if self.visit(child, **cell_label_kwargs):
                self.pop()
        return False

    def visit_table(self, node: "MdTable", **kwargs) -> bool:
        self.visiting_table = True
        table_head = node["children"][0]
        self.push(MarkdownTable())

        # Table head row
        head_kwargs = {k: v for k, v in kwargs.items()}
        head_kwargs.update({"bold": True, "font_hinting": None, "halign": "center"})
        self.push(MarkdownRow(is_head=True))
        for cell in table_head["children"]:
            if self.visit(cell, **head_kwargs):
                self.pop()
        self.pop()
        Logger.debug("Start Table Body")

        del head_kwargs

        rows = node["children"][1]["children"]
        for row_idx, row in enumerate(rows):
            self.push(MarkdownRow(is_head=False))
            for cell in row["children"]:
                if self.visit(cell, **kwargs):
                    self.pop()
            self.pop()
        return True

    def visit_paragraph(self, node: "MdParagraph", **kwargs) -> bool:
        if not node["children"]:
            return False
        self.push(MarkdownBlock())
        for child in node["children"]:
            if self.visit(child, **kwargs):
                self.pop()
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
        if self.visiting_table:
            self.push(
                MarkdownCellLabel(
                    text=self.pop_bbcode(node["text"]),
                    **{**kwargs, **{"font_hinting": "mono"}},
                )
            )
        else:
            self.push(MarkdownCodeSpan(text=self.pop_bbcode(node["text"]), **kwargs))
        return True

    def visit_text(self, node: "MdText", **kwargs) -> bool:
        if isinstance(self.current_list[-1], MarkdownHeading):
            md_widget = self.pop()
            md_widget.text = self.pop_bbcode(node["text"])
            if kwargs:
                for k, v in kwargs.items():
                    setattr(md_widget, k, v)
            self.push(md_widget)
            return False
        elif self.visiting_table:
            self.push(MarkdownCellLabel(text=self.pop_bbcode(node["text"]), **kwargs))
            return True
        else:
            self.push(Label(text=self.pop_bbcode(node["text"]), **kwargs))
            return True

    def visit_block_quote(self, node: "MdBlockQuote", **kwargs) -> bool:
        self.push(MarkdownBlockQuote(text_content=get_md_node_text(node), **kwargs))
        return True

    def visit_newline(self, node: "MdNewLine", **kwargs) -> bool:
        return False

    def visit_strong(self, node: "MdTextStrong", **kwargs):
        self.push_bbcode("[b]")
        widget_kwargs = {k: v for k, v in kwargs.items()}
        widget_kwargs.update({"markup": True})
        for child in node["children"]:
            if self.visit(child, **widget_kwargs):
                self.pop()
        return False

    def visit_emphasis(self, node: "MdTextEmphasis", **kwargs):
        self.push_bbcode("[i]")
        widget_kwargs = {k: v for k, v in kwargs.items()}
        widget_kwargs.update({"markup": True})
        for child in node["children"]:
            if self.visit(child, **widget_kwargs):
                self.pop()
        return False

    def visit_generic(self, node, **kwargs):
        node_type = node.get("type")
        Logger.info(f"Skipping {node_type if node_type else node} - No Handler")
