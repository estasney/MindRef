from __future__ import annotations

from kivy.logger import Logger
from kivy.properties import Property

from mindref.lib.domain.md_parser_types import (
    TMdInlineTypes,
)
from mindref.lib.widgets.behavior.inline_behavior import TextSnippet


class MarkdownLabelParsingMixin:
    """
    The purpose of this mixin class is to handle the imperfect mapping of Markdown AST to Kivy Layouts/Widgets.

    Internally, this assumes usage of `LabelHighlightInline`

    Notes
    -----
    Subclasses own how snippets are stored, and expose them through
    'get_snippets' and 'set_snippets'.

    """

    open_bbcode_tag: Property[str]

    def get_snippets(self) -> list[TextSnippet]:
        raise NotImplementedError

    def set_snippets(self, value: list[TextSnippet]) -> None:
        raise NotImplementedError

    def __init__(self):
        self.set_snippets([])
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
                    case "text" | "inline_html":
                        self.set_snippets(
                            [
                                *self.get_snippets(),
                                TextSnippet(text, highlight_tag=None),
                            ]
                        )
                        return None
                    case "kbd":
                        self.set_snippets(
                            [
                                *self.get_snippets(),
                                TextSnippet(text, highlight_tag="kbd"),
                            ]
                        )
                        return None
                    case "codespan":
                        self.set_snippets(
                            [
                                *self.get_snippets(),
                                TextSnippet(text, highlight_tag="hl"),
                            ]
                        )
                        return None
            case _:
                Logger.warning(
                    f"{type(self).__name__}: visit - unhandled node type {node}"
                )
                return None
