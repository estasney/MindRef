from kivy.properties import ListProperty, ObjectProperty, OptionProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from widgets.markdown.markdown_parsing_mixin import MarkdownLabelParsingMixin


class MarkdownLabelBase(BoxLayout, MarkdownLabelParsingMixin):
    label = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets = ListProperty()
    halign = OptionProperty(
        "auto", options=["left", "center", "right", "justify", "auto"]
    )
    valign = OptionProperty("bottom", options=["bottom", "middle", "center", "top"])

    def __init__(self, **kwargs):
        super(MarkdownLabelBase, self).__init__(**kwargs)
