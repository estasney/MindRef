from __future__ import annotations

from typing import Optional, Protocol, TYPE_CHECKING

from kivy import Logger
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget

from widgets.behavior.inline_behavior import TextSnippet

if TYPE_CHECKING:
    from domain.md_parser_types import (
        MD_INLINE_TYPES,
        MdText,
        MdCodeSpan,
        MdTextStrong,
        MdTextEmphasis,
    )


class VisitorProtocol(Protocol):
    def pop(self):
        ...

    def push(self, node: Widget | Layout):
        ...


class InterceptingWidgetProtocol(Protocol):
    def handle_intercept(self, node: "MD_INLINE_TYPES"):
        ...


class InterceptingWidgetMixin:
    """
    The purpose of this mixin class is to handle the imperfect mapping of Markdown AST to Kivy Layouts/Widgets.

    For example, when we've encountered a Heading that is also a Codespan. In this case 3 nodes become 1 Widget:
        - Heading -> Sizing, Bold
        - CodeSpan -> Mono-size font, code highlighting
        - Text -> Content

    """

    text: str
    raw_text: str
    is_codespan: bool
    open_bbcode_tag: Optional[str]

    def __init__(self):
        for name in ("text", "raw_text", "is_codespan", "open_bbcode_tag"):
            if not hasattr(self, name):
                raise AttributeError(
                    f"Expected {self.__class__.__name__} to have Property: '{name}'"
                )

    def handle_intercept(self, node: "MD_INLINE_TYPES"):
        if node["type"] == "text":
            node: "MdText"
            self.raw_text = f"{self.raw_text} {node['text']}{self.open_bbcode_tag if self.open_bbcode_tag else ''}".strip()
            self.open_bbcode_tag = ""
        elif node["type"] == "codespan":
            node: "MdCodeSpan"
            self.is_codespan = True
            self.raw_text = f"{self.raw_text} {node['text']}{self.open_bbcode_tag if self.open_bbcode_tag else ''}".strip()
            self.open_bbcode_tag = ""
        elif node["type"] == "strong":
            node: "MdTextStrong"
            self.raw_text = f"{self.raw_text} [b]".strip()
            self.open_bbcode_tag = "[/b]"
        elif node["type"] == "emphasis":
            node: "MdTextEmphasis"
            self.raw_text = f"{self.raw_text} [i]".strip()
            self.open_bbcode_tag = "[/i]"
        else:
            Logger.warn(f"Unhandled node {node}")


class InterceptingInlineWidgetMixin:
    """
    The purpose of this mixin class is to handle the imperfect mapping of Markdown AST to Kivy Layouts/Widgets.

    Internally, this assumes usage of `LabelHighlightInline`

    """

    snippets: list["TextSnippet"]
    open_bbcode_tag: str

    def __init__(self):
        for name in ("snippets",):
            if not hasattr(self, name):
                raise AttributeError(
                    f"Expected {self.__class__.__name__} to have Property: '{name}'"
                )
        self.open_bbcode_tag = ""

    def handle_intercept(self, node: "MD_INLINE_TYPES"):
        if node["type"] == "text":
            node: "MdText"
            if self.open_bbcode_tag:
                text = (
                    f"[{self.open_bbcode_tag}]{node['text']}[/{self.open_bbcode_tag}]"
                )
            else:
                text = node["text"]
            self.snippets.append(TextSnippet(text, highlight=False))
            self.open_bbcode_tag = ""
        elif node["type"] == "codespan":
            node: "MdCodeSpan"
            if self.open_bbcode_tag:
                text = (
                    f"[{self.open_bbcode_tag}]{node['text']}[/{self.open_bbcode_tag}]"
                )
            else:
                text = node["text"]
            self.snippets.append(TextSnippet(text, highlight=True))
            self.open_bbcode_tag = ""
        elif node["type"] == "strong":
            node: "MdTextStrong"
            self.open_bbcode_tag = "b"
        elif node["type"] == "emphasis":
            node: "MdTextEmphasis"
            self.open_bbcode_tag = "i"
        else:
            Logger.warn(f"Unhandled node {node}")


class WidgetIntercept:
    def __init__(self, visitor: VisitorProtocol, widget: InterceptingWidgetProtocol):
        self.visitor = visitor
        self.widget = widget
        self.visitor_push = visitor.push
        self.visitor_pop = visitor.pop

    def intercept_push(self, widget: "MD_INLINE_TYPES"):
        self.widget.handle_intercept(widget)
        return False

    def intercept_pop(self):
        return None

    def __enter__(self):
        self.visitor.push = self.intercept_push
        self.visitor.pop = self.intercept_pop
        self.visitor.has_intercept = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.visitor.push = self.visitor_push
        self.visitor.pop = self.visitor_pop
        self.visitor.has_intercept = False
