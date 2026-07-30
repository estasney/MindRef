from __future__ import annotations

from kivy.properties import (
    ListProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.widgets.behavior.inline_behavior import (
    LabelHighlightInline,
    TextSnippet,
)
from mindref.lib.widgets.markdown.markdown_parsing_mixin import (
    MarkdownLabelParsingMixin,
)


class MarkdownLabelBase(BoxLayout, MarkdownLabelParsingMixin):
    label: ObjectProperty[LabelHighlightInline] = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets: ListProperty[TextSnippet] = ListProperty()
    halign = OptionProperty(
        "auto", options=["left", "center", "right", "justify", "auto"]
    )
    valign = OptionProperty("bottom", options=["bottom", "middle", "center", "top"])

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)

    def get_snippets(self) -> list[TextSnippet]:
        return self.snippets

    def set_snippets(self, value: list[TextSnippet]) -> None:
        self.snippets = value
