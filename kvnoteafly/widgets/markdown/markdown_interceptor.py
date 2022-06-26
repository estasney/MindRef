from __future__ import annotations

from typing import Optional, Protocol, TYPE_CHECKING

from kivy import Logger
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget

if TYPE_CHECKING:
    from domain import (
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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.visitor.push = self.visitor_push
        self.visitor.pop = self.visitor_pop
