from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from kivy.logger import Logger

from mindref.lib.domain.md_parser_types import (
    TMdInlineTypes,
)
from mindref.lib.widgets.behavior.inline_behavior import TextSnippet

if TYPE_CHECKING:
    from kivy.uix.layout import Layout
    from kivy.uix.widget import Widget


class VisitorProtocol(Protocol):
    def pop(self): ...

    def push(self, node: Widget | Layout): ...


class MarkdownLabelParsingProtocol(Protocol):
    """
    Protocol specifying expected methods for a Widget with InterceptingWidgetInlineMixin
    """

    __name__: str

    def handle_intercept(self, node: TMdInlineTypes): ...

    def handle_intercept_exit(self): ...


class MarkdownLabelParsingMixin:
    """
    The purpose of this mixin class is to handle the imperfect mapping of Markdown AST to Kivy Layouts/Widgets.

    Internally, this assumes usage of `LabelHighlightInline`

    Notes
    -----
    Subclasses must have an attribute 'snippets' as a ListProperty

    """

    snippets: list[TextSnippet]
    open_bbcode_tag: str

    def __init__(self):
        self.snippets = []
        self.open_bbcode_tag = ""

    def visit(self, node: TMdInlineTypes) -> TMdInlineTypes | None:
        match node:
            case {"type": "strong", "children": list()}:
                matched_node = node
                self.open_bbcode_tag = "b"
                for child in matched_node["children"]:
                    if unh := self.visit(child):
                        return unh
                return None
            case {"type": "emphasis", "children": list()}:
                matched_node = node
                self.open_bbcode_tag = "i"
                for child in matched_node["children"]:
                    if unh := self.visit(child):
                        return unh
                return None
            case {
                "type": "text" | "kbd" | "codespan" | "inline_html" as span_type,
                "text": str(),
            }:
                if self.open_bbcode_tag:
                    text = f"[{self.open_bbcode_tag}]{node['text']}[/{self.open_bbcode_tag}]"
                    self.open_bbcode_tag = ""
                else:
                    text = node["text"]
                match span_type:
                    # We copy snippets in case cls.snippets is an AliasProperty
                    # In this case, snippets.append would not trigger a change
                    case "text" | "inline_html":
                        self.snippets = [
                            *self.snippets[:],
                            TextSnippet(text, highlight_tag=None),
                        ]
                        return None
                    case "kbd":
                        self.snippets = [
                            *self.snippets[:],
                            TextSnippet(text, highlight_tag="kbd"),
                        ]

                        return None
                    case "codespan":
                        self.snippets = [
                            *self.snippets[:],
                            TextSnippet(text, highlight_tag="hl"),
                        ]
                        return None
            case _:
                Logger.warning(
                    f"{type(self).__name__}: visit - unhandled node type {node}"
                )
                return None
