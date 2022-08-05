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
        MdInlineKeyboard,
    )


class VisitorProtocol(Protocol):
    def pop(self):
        ...

    def push(self, node: Widget | Layout):
        ...


class InterceptingWidgetProtocol(Protocol):
    """
    Protocol specifying expected methods for a Widget with InterceptingWidgetInlineMixin
    """

    def handle_intercept(self, node: "MD_INLINE_TYPES"):
        ...

    def handle_intercept_exit(self):
        ...


class InterceptingInlineWidgetMixin:
    """
    The purpose of this mixin class is to handle the imperfect mapping of Markdown AST to Kivy Layouts/Widgets.

    Internally, this assumes usage of `LabelHighlightInline`

    Notes
    -----
    Subclasses must have an attribute 'snippets' as a ListProperty

    """

    snippets: list["TextSnippet"]
    open_bbcode_tag: str

    def __new__(cls: InterceptingWidgetProtocol, *args, **kwargs):
        for name in ("snippets",):
            if not hasattr(cls, name):
                obj_name = kwargs.get("name", cls.__name__)
                raise AttributeError(f"{obj_name} must have ")

    def __init__(self):
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
            self.snippets.append(TextSnippet(text, highlight_tag=None))
            self.open_bbcode_tag = ""
        elif node["type"] == "kbd":
            node: "MdCodeSpan"
            if self.open_bbcode_tag:
                text = (
                    f"[{self.open_bbcode_tag}]{node['text']}[/{self.open_bbcode_tag}]"
                )
            else:
                text = node["text"]
            self.snippets.append(TextSnippet(text, highlight_tag="kbd"))
            self.open_bbcode_tag = ""
        elif node["type"] == "codespan":
            node: "MdInlineKeyboard"
            if self.open_bbcode_tag:
                text = (
                    f"[{self.open_bbcode_tag}]{node['text']}[/{self.open_bbcode_tag}]"
                )
            else:
                text = node["text"]
            self.snippets.append(TextSnippet(text, highlight_tag="hl"))
            self.open_bbcode_tag = ""
        elif node["type"] == "strong":
            node: "MdTextStrong"
            self.open_bbcode_tag = "b"
        elif node["type"] == "emphasis":
            node: "MdTextEmphasis"
            self.open_bbcode_tag = "i"
        else:
            Logger.warn(f"Unhandled node {node}")

    def handle_intercept_exit(self):
        ...


class WidgetIntercept:
    """
    Context Manager managing InterceptingWidgets entry and exist

    Examples
    --------
    ```python
    some_widget = MarkdownHeading()  # Widget that follows InterceptingWidgetProtocol

    with WidgetIntercept(visitor=self, widget=some_widget):
        # Override `self`'s `visit` method
        for node in node['children']:
            self.visit(node)
    # Restore original `visit` method
    ```

    """

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
        self.widget.handle_intercept_exit()
