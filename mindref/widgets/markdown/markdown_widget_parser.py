from __future__ import annotations

from typing import cast, Optional, Container

from kivy import Logger
from kivy.uix.widget import Widget
from toolz import get_in

from domain.md_parser_types import (
    MdHeading,
    MdParagraph,
    MdBlockCode,
    MdCodeSpan,
    MdBlockQuote,
    MdBlockText,
    MdTable,
    MdTableHeadCell,
    MdTableBodyRow,
    MdTableBodyCell,
    MdTableHead,
    MdTextStrong,
    MdInlineKeyboard,
    MdListOrdered,
    MdListUnordered,
    MdListItem,
    MdNewLine,
)
from widgets.markdown.block.markdown_block import MarkdownHeading, MarkdownBlock
from widgets.markdown.code.code_span import MarkdownCodeSpan
from widgets.markdown.code.markdown_code import MarkdownCode
from widgets.markdown.list.markdown_list import MarkdownList
from widgets.markdown.list.markdown_list_item import MarkdownListItem
from widgets.markdown.markdown_parsing_mixin import MarkdownLabelParsingMixin
from widgets.markdown.paragraph.blocks import MarkdownBlockQuote
from widgets.markdown.table.markdown_table import (
    MarkdownTable,
    MarkdownRow,
    MarkdownCell,
)


class MarkdownWidgetParser:
    state: Widget | None
    current_state: Widget | None

    def __init__(self, parent: MarkdownWidgetParser | None = None):
        self.parent = parent
        self.state = None

    @staticmethod
    def _report_nested_lists(
        data, idx: Optional[tuple[int | str, ...]], report_nodes: Container[str]
    ):
        """
        Find any nodes with children, and notify return a tuple of keys/index to find them from `data`
        """
        report = MarkdownWidgetParser._report_nested_lists
        reports = []
        match data:
            case {"type": str(node)} if node in report_nodes:
                if idx:
                    reports.append(idx)
        match data:
            case {"children": list(children)}:
                # Don't report, but still check children
                for i, child in enumerate(children):
                    child_idx = (
                        tuple((*idx, "children", i))
                        if idx is not None
                        else tuple(("children", i))
                    )
                    child_report = report(child, child_idx, report_nodes)
                    if child_report:
                        reports.extend(child_report)
                return reports
            case _:
                return reports

    def parse(self, node: dict) -> Widget | None:
        def delegate_parse(n):
            parser_delegate = MarkdownWidgetParser(parent=self)
            delg_result = parser_delegate.parse(n)
            if delg_result:
                self.state.add_widget(delg_result)

        def parse_for_result(n):
            parser_delegate = MarkdownWidgetParser(parent=self)
            return parser_delegate.parse(n)

        match node:
            case ({"type": "heading", "level": int(level), "children": list()}):
                parsed_node = cast(MdHeading, node)
                widget = MarkdownHeading(level=level)
                for child in parsed_node["children"]:
                    widget.visit(child)
                match self.state:
                    case Widget():
                        self.state.add_widget(widget)
                    case None:
                        self.state = widget
            case {
                "type": "strong" | "emphasis",
                "children": list(),
            } if self.state and issubclass(self.state, MarkdownLabelParsingMixin):
                self.state.visit(node)

            case {
                "type": "text" | "kbd" | "codespan" | "inline_html",
                "text": str(),
            } if self.state and issubclass(self.state, MarkdownLabelParsingMixin):
                self.state.visit(node)

            case {"type": "paragraph" | "block_text" | "strong", "children": list()}:
                parsed_node = cast(MdParagraph | MdBlockText | MdTextStrong, node)
                match self.state:
                    case MarkdownListItem():
                        for child in parsed_node["children"]:
                            self.state.visit(child)
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        self.state = MarkdownBlock()
                        for child in parsed_node["children"]:
                            if unh := self.state.visit(child) and self.parent:
                                self.parent.state.visit(unh)

            case {"type": "kbd", "text": str(kbd_key)}:
                parsed_node = cast(MdInlineKeyboard, node)
                match self.state:
                    case MarkdownLabelParsingMixin():
                        self.state.visit(parsed_node)
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        Logger.error(
                            f"{type(self).__name__}: parse - fallthrough kbd {kbd_key}"
                        )

            case {"type": "block_quote", "children": list()}:
                parsed_node = cast(MdBlockQuote, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        self.state = MarkdownBlockQuote()
                        for child in parsed_node["children"]:
                            if unh := self.state.visit(child) and self.parent:
                                self.parent.parse(unh)

            case {"type": "block_code", "text": str(node_text), "info": lexer}:
                parsed_node = cast(MdBlockCode, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        widget = MarkdownCode(lexer=lexer, text_content=node_text)
                        self.state = widget

            case {"type": "codespan", "text": str(node_text)}:
                parsed_node = cast(MdCodeSpan, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        widget = MarkdownCodeSpan(text=node_text)
                        self.state = widget
            case {
                "type": "table",
                "children": [
                    {"type": "table_head", "children": list()} as table_head,
                    {"type": "table_body", "children": list(table_body)},
                ],
            }:
                """
                Tables Should always have 2 children:
                  table_head
                    - table_cell
                  table_body
                    - table_row
                        - table_cell

                """
                parsed_node = cast(MdTable, node)
                match self.state:
                    case Widget():
                        Logger.info(
                            f"{type(self).__name__}: Trying to add a nested table"
                        )
                        delegate_parse(parsed_node)
                    case None:
                        self.state = MarkdownTable()
                        table_head_widget = parse_for_result(table_head)
                        if not table_head_widget:
                            Logger.warning(
                                f"{type(self).__name__}: parse failed - {table_head}"
                            )
                            return self.state
                        self.state.add_widget(table_head_widget)
                        for row in table_body:
                            table_body_widget = parse_for_result(row)
                            if not table_body_widget:
                                Logger.warning(
                                    f"{type(self).__name__}: parse failed - {table_body}"
                                )
                                continue
                            self.state.add_widget(table_body_widget)

            case {"type": "table_head", "children": list(head_cells)}:
                parsed_node = cast(MdTableHead, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        self.state = MarkdownRow()
                        for cell in head_cells:
                            delegate_parse(cell)

            case {"type": "table_row", "children": list(row_cells)}:
                parsed_node = cast(MdTableBodyRow, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        self.state = MarkdownRow()
                        for cell in row_cells:
                            delegate_parse(cell)

            case {
                "type": "table_cell",
                "is_head": bool(is_head),
                "align": cell_align,
                "children": list(children),
            }:
                parsed_node = cast(MdTableHeadCell | MdTableBodyCell, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        cell_align = cell_align if cell_align else "center"
                        cell_bold = is_head
                        self.state = MarkdownCell(
                            **{"halign": cell_align, "bold": cell_bold}
                        )
                        for cell in children:
                            self.state.visit(cell)
            case {"type": "list", "children": list(), "level": 1}:
                parsed_node = cast(MdListOrdered | MdListUnordered, node)

                # Bubble up any nested lists
                node_reports = MarkdownWidgetParser._report_nested_lists(
                    parsed_node,
                    None,
                    {
                        "list_item",
                    },
                )
                bubbled_children = [get_in(nr, parsed_node) for nr in node_reports]

                match self.state:
                    case None:
                        self.state = MarkdownList()
                        for child in bubbled_children:
                            delegate_parse(child)
                    case MarkdownList():
                        for item in bubbled_children:
                            delegate_parse(item)
                    case Widget():
                        delegate_parse(parsed_node)

            case {"type": "list_item", "children": list(children), "level": int(level)}:
                parsed_node = cast(MdListItem, node)
                match self.state:
                    case Widget():
                        delegate_parse(parsed_node)
                    case None:
                        self.state = MarkdownListItem(level=level)
                        for child in children:
                            self.parse(child)

            case {"type": "newline"}:
                parsed_node = cast(MdNewLine, node)
                match self.state:
                    case Widget() if hasattr(self.state, "text"):
                        self.state.text += "\n"

            case _:
                Logger.warning(f"{type(self).__name__}: parse - Unhandled node {node}")

        return self.state
