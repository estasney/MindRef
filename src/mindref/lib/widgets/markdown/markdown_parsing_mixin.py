from __future__ import annotations

from typing import Protocol, cast

from kivy import Logger
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget

from mindref.lib.domain.md_parser_types import (
    MD_INLINE_TYPES,
    MdTextEmphasis,
    MdTextStrong,
)
from mindref.lib.widgets.behavior.inline_behavior import TextSnippet


class VisitorProtocol(Protocol):
    def pop(self): ...

    def push(self, node: Widget | Layout): ...


class MarkdownLabelParsingProtocol(Protocol):
    """
    Protocol specifying expected methods for a Widget with InterceptingWidgetInlineMixin
    """

    __name__: str

    def handle_intercept(self, node: MD_INLINE_TYPES): ...

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

    def __new__(cls: MarkdownLabelParsingProtocol, *args, **kwargs):
        for name in ("snippets", "open_bbcode_tag"):
            if not hasattr(cls, name):
                obj_name = kwargs.get("name", cls.__name__)
                raise AttributeError(f"{obj_name} must have ")

    def __init__(self):
        self.open_bbcode_tag = ""

    def visit(self, node: MD_INLINE_TYPES) -> MD_INLINE_TYPES | None:
        match node:
            case {"type": "strong", "children": list()}:
                matched_node = cast(MdTextStrong, node)
                self.open_bbcode_tag = "b"
                for child in matched_node["children"]:
                    if unh := self.visit(child):
                        return unh
                return None
            case {"type": "emphasis", "children": list()}:
                matched_node = cast(MdTextEmphasis, node)
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
                            f"{type(self).__name__}: visit - unhandled highlight type {span_type}"
                        )
                        return node

            case _:
                Logger.warning(
                    f"{type(self).__name__}: visit - unhandled node type {node}"
                )


class WidgetIntercept:
    """
    Context Manager managing InterceptingWidgets entry and exist

    Examples
    --------
    ```python
    some_widget = MarkdownHeading()  # Widget that follows MarkdownLabelParsingProtocol

    with WidgetIntercept(visitor=self, widget=some_widget):
        # Override `self`'s `visit` method
        for node in node['children']:
            self.visit(node)
    # Restore original `visit` method
    ```

    """

    def __init__(self, visitor: VisitorProtocol, widget: MarkdownLabelParsingProtocol):
        self.visitor = visitor
        self.widget = widget
        self.visitor_push = visitor.push
        self.visitor_pop = visitor.pop

    def intercept_push(self, widget: MD_INLINE_TYPES):
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
