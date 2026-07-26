from __future__ import annotations

from typing import TYPE_CHECKING

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from mindref.lib.widgets.behavior import DebugBoxLayout
from mindref.lib.widgets.markdown.markdown_widget_parser import MarkdownWidgetParser

if TYPE_CHECKING:
    from mindref.lib.domain.md_parser_types import TMdDocument

Builder.load_string(
    """
<MarkdownDocumentLayout>:
    orientation: "vertical"
    height: self.minimum_height
    size_hint_y: None
    pos_hint: {"center_x": 0, "y": 0}
"""
)


class MarkdownDocumentLayout(DebugBoxLayout):
    """
    A layout for displaying markdown content.

    This layout is designed to hold markdown content in a scrollable format.
    It uses a GridLayout to arrange the content vertically.
    """

    document: ObjectProperty[TMdDocument] = ObjectProperty()

    def on_document(
        self, _instance: MarkdownDocumentLayout, value: TMdDocument
    ) -> None:
        self.clear_widgets()
        for child in value:
            parser = MarkdownWidgetParser()
            child_result = parser.parse(child)
            if child_result:
                self.add_widget(child_result)
