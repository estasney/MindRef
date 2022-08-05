from typing import TYPE_CHECKING

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line

from utils import import_kv
from widgets.markdown.markdown_interceptor import InterceptingInlineWidgetMixin

import_kv(__file__)

from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    ListProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

if TYPE_CHECKING:
    pass


class MarkdownTable(GridLayout):
    pass


class MarkdownRow(BoxLayout):
    ...

    def __init__(self, **kwargs):
        super(MarkdownRow, self).__init__(**kwargs)
        fbind = self.fbind
        draw = self.schedule_draw
        fbind("x", draw)
        fbind("y", draw)
        fbind("width", draw)
        fbind("height", draw)
        fbind("children", draw)

    def schedule_draw(self, instance, value):
        Clock.schedule_once(self.draw_cell_border)
        return True

    def draw_cell_border(self, dt):
        with self.canvas.before:
            self.canvas.before.clear()
            Color(rgba=App.get_running_app().colors["Dark"])
            Line(width=1.2, rectangle=(self.x, self.y, self.width, self.height))
            for child in self.children[:-1]:
                Line(width=1.2, rectangle=(self.x, self.y, child.width, self.height))


class MarkdownCell(BoxLayout, InterceptingInlineWidgetMixin):
    label = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets = ListProperty()
    halign = OptionProperty(
        "auto", options=["left", "center", "right", "justify", "auto"]
    )
    valign = OptionProperty("center", options=["bottom", "middle", "center", "top"])
    bold = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fbind = self.fbind
        label = self.label
        fbind("halign", label.setter("halign"))
        fbind("valign", label.setter("valign"))
        fbind("bold", self.handle_bold)

    def handle_bold(self, *args):
        if self.bold:
            self.open_bbcode_tag = "b"
        else:
            self.open_bbcode_tag = ""
