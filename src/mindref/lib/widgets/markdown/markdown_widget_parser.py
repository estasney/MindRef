from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from kivy.logger import Logger
from kivy.uix.widget import Widget

from mindref.lib.widgets.markdown.block.markdown_block import (
    MarkdownBlock,
    MarkdownHeading,
    MarkdownThematicBreak,
)
from mindref.lib.widgets.markdown.code.code_span import MarkdownCodeSpan
from mindref.lib.widgets.markdown.code.markdown_code import MarkdownCode
from mindref.lib.widgets.markdown.list.markdown_list import MarkdownList
from mindref.lib.widgets.markdown.list.markdown_list_item import MarkdownListItem
from mindref.lib.widgets.markdown.markdown_parsing_mixin import (
    MarkdownLabelParsingMixin,
)
from mindref.lib.widgets.markdown.paragraph.blocks import MarkdownBlockQuote
from mindref.lib.widgets.markdown.table.markdown_table import (
    MarkdownCell,
    MarkdownRow,
    MarkdownTable,
)

if TYPE_CHECKING:
    from collections.abc import Container, Iterator

    from mindref.lib.domain.md_parser_types import TMdTags, TMdTypes


@runtime_checkable
class TextWidget(Protocol):
    text: str


class MarkdownWidgetParser:
    parent: MarkdownWidgetParser | None
    state: Widget | None

    def __init__(self, parent: MarkdownWidgetParser | None = None) -> None:
        self.parent = parent
        self.state = None

    @staticmethod
    def _report_nested_lists(
        data: TMdTypes, report_nodes: Container[TMdTags]
    ) -> Iterator[TMdTypes]:
        """
        Yield every descendant of `data` whose type is in `report_nodes`, pre-order
        """
        report = MarkdownWidgetParser._report_nested_lists
        match data:
            case {"children": list(children)}:
                for child in children:
                    match child:
                        case {"type": str(tag)} if tag in report_nodes:
                            yield child
                        case _:
                            pass
                    yield from report(child, report_nodes)
            case _:
                pass

    def parse(self, node: TMdTypes) -> Widget | None:
        def delegate_parse(n: TMdTypes, target: Widget) -> None:
            parser_delegate = MarkdownWidgetParser(parent=self)
            delg_result = parser_delegate.parse(n)
            if delg_result:
                target.add_widget(delg_result)

        def parse_for_result(n: TMdTypes) -> Widget | None:
            parser_delegate = MarkdownWidgetParser(parent=self)
            return parser_delegate.parse(n)

        match node:
            case {"type": "heading", "level": int(level), "children": list()}:
                widget = MarkdownHeading(level=level)
                for child in node["children"]:
                    widget.visit(child)
                match self.state:
                    case Widget():
                        self.state.add_widget(widget)
                    case None:
                        self.state = widget
            case {
                "type": "strong" | "emphasis",
                "children": list(),
            } if isinstance(self.state, MarkdownLabelParsingMixin):
                self.state.visit(node)

            case {
                "type": "text" | "kbd" | "codespan" | "inline_html",
                "text": str(),
            } if isinstance(self.state, MarkdownLabelParsingMixin):
                self.state.visit(node)

            case {"type": "paragraph" | "block_text" | "strong", "children": list()}:
                match self.state:
                    case MarkdownListItem():
                        for child in node["children"]:
                            self.state.visit(child)
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        self.state = MarkdownBlock()
                        for child in node["children"]:
                            if (unh := self.state.visit(child)) and self.parent:
                                self.parent.parse(unh)

            case {"type": "kbd", "text": str(kbd_key)}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        Logger.error(
                            f"{type(self).__name__}: parse - fallthrough kbd {kbd_key}"
                        )

            case {"type": "block_quote", "children": list()}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        self.state = MarkdownBlockQuote()
                        for child in node["children"]:
                            delegate_parse(child, self.state)

            case {"type": "block_code", "text": str(node_text), "info": lexer}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        widget = MarkdownCode(lexer=lexer, text_content=node_text)
                        self.state = widget

            case {"type": "codespan", "text": str(node_text)}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        widget = MarkdownCodeSpan(text=node_text)
                        self.state = widget

            case {"type": "thematic_break"}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        self.state = MarkdownThematicBreak()

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
                match self.state:
                    case Widget():
                        Logger.info(
                            f"{type(self).__name__}: Trying to add a nested table"
                        )
                        delegate_parse(node, self.state)
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
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        self.state = MarkdownRow()
                        for cell in head_cells:
                            delegate_parse(cell, self.state)

            case {"type": "table_row", "children": list(row_cells)}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        self.state = MarkdownRow()
                        for cell in row_cells:
                            delegate_parse(cell, self.state)

            case {
                "type": "table_cell",
                "is_head": bool(is_head),
                "align": cell_align,
                "children": list(children),
            }:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        cell_align = cell_align or "center"
                        cell_bold = is_head
                        self.state = MarkdownCell(halign=cell_align, bold=cell_bold)
                        for cell in children:
                            self.state.visit(cell)
            case {"type": "list", "children": list(), "level": 1}:
                # Bubble up any nested lists
                bubbled_children = MarkdownWidgetParser._report_nested_lists(
                    node, {"list_item"}
                )

                match self.state:
                    case None:
                        self.state = MarkdownList()
                        for child in bubbled_children:
                            delegate_parse(child, self.state)
                    case MarkdownList():
                        for item in bubbled_children:
                            delegate_parse(item, self.state)
                    case Widget():
                        delegate_parse(node, self.state)

            case {"type": "list_item", "children": list(children), "level": int(level)}:
                match self.state:
                    case Widget():
                        delegate_parse(node, self.state)
                    case None:
                        self.state = MarkdownListItem(level=level)
                        for child in children:
                            self.parse(child)

            case {"type": "newline"}:
                match self.state:
                    case Widget() if isinstance(self.state, TextWidget):
                        self.state.text += "\n"
                    case _:
                        pass

            case _:
                Logger.warning(f"{type(self).__name__}: parse - Unhandled node {node}")

        return self.state
