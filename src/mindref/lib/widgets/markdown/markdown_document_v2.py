from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.widgets.markdown.markdown_widget_parser import MarkdownWidgetParser

Builder.load_string(
    """
<MarkdownDocumentLayout>:
    orientation: "vertical"
    height: self.minimum_height
    size_hint_y: None
    pos_hint: {"center_x": 0, "y": 0}
    
    
"""
)


class MarkdownDocumentLayout(BoxLayout):
    """
    A layout for displaying markdown content.

    This layout is designed to hold markdown content in a scrollable format.
    It uses a GridLayout to arrange the content vertically.
    """

    debug_layout = BooleanProperty()
    document = ObjectProperty()
    """
    The GridLayout that holds the markdown content.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_parent(self, _instance, value):
        _instance.bind(width=self.setter("width"))

    def on_document(self, _instance, value):
        for child in value:
            parser = MarkdownWidgetParser()
            child_result = parser.parse(child)
            if child_result:
                self.add_widget(child_result)
