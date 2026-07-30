from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from mindref.lib.utils import get_app
from mindref.lib.widgets.behavior.inline_behavior import TextSnippet
from mindref.lib.widgets.markdown.markdown_parsing_mixin import (
    MarkdownLabelParsingMixin,
)

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import LabelHighlightInline mindref.lib.widgets.behavior

<MarkdownTable>:
    size_hint_y: None
    cols: 1
    height: self.minimum_height
<MarkdownRow>:
    orientation: 'horizontal'
    padding: dp(4),dp(2)
    size_hint_y: None
    size_hint_x: 1
    height: self.minimum_height


<MarkdownCell>:
    orientation: 'horizontal'
    size_hint_y: None
    height: self.minimum_height
    size_hint_x: 1
    padding: (dp(10), dp(2), dp(10), dp(2))
    label: label
    LabelHighlightInline:
        id: label
        snippets: root.snippets
        bg_color: app.colors['Primary']
        highlight_color: app.colors['Codespan']
        valign: 'center'
        halign: 'left'
        height: self.texture_size[1]
        size_hint_y: None
""")


class MarkdownTable(GridLayout):
    pass


class MarkdownRow(BoxLayout):
    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        fbind = self.fbind
        draw = self.schedule_draw
        fbind("x", draw)
        fbind("y", draw)
        fbind("width", draw)
        fbind("height", draw)
        fbind("children", draw)

    def schedule_draw(self, *_args):
        Clock.schedule_once(self.draw_cell_border)
        return True

    def draw_cell_border(self, *_args):
        with self.canvas.before:
            self.canvas.before.clear()
            Color(rgba=get_app().colors["Dark"])
            Line(width=1.2, rectangle=(self.x, self.y, self.width, self.height))
            for child in self.children[:-1]:
                Line(width=1.2, rectangle=(self.x, self.y, child.width, self.height))


class MarkdownCell(BoxLayout, MarkdownLabelParsingMixin):
    label = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets = ListProperty()
    halign = OptionProperty(
        "auto", options=["left", "center", "right", "justify", "auto"]
    )
    valign = OptionProperty("center", options=["bottom", "middle", "center", "top"])
    bold = BooleanProperty(False)

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        fbind = self.fbind
        label = self.label
        fbind("halign", label.setter("halign"))
        fbind("valign", label.setter("valign"))
        fbind("bold", self.handle_bold)

    def get_snippets(self) -> list[TextSnippet]:
        return self.snippets

    def set_snippets(self, value: list[TextSnippet]) -> None:
        self.snippets = value

    def handle_bold(self, *_args):
        if self.bold:
            self.open_bbcode_tag = "b"
        else:
            self.open_bbcode_tag = ""
