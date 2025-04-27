from kivy import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from mindref.lib.widgets.behavior import DebugBoxLayout, DebugFloatLayout
from mindref.lib.widgets.markdown.markdown_widget_parser import MarkdownWidgetParser

Builder.load_string(
    """
<MarkdownDocumentLayout>:
    debug_layout: True
    orientation: "vertical"
    height: self.minimum_height
    padding: [dp(0), dp(0), dp(80), dp(0)]
    size_hint_y: None
    size_hint_x: 1
    pos_hint: {"x": 0.5, "y": 0}
    
    
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
