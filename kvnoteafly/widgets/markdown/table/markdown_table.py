from typing import TYPE_CHECKING

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.graphics.context_instructions import Color

from utils import import_kv
from widgets.markdown.markdown_interceptor import InterceptingWidgetMixin

import_kv(__file__)

from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from widgets.behavior.label_behavior import LabelHighlight

if TYPE_CHECKING:
    pass


class MarkdownTable(GridLayout):
    pass


class MarkdownCellLabel(LabelHighlight, InterceptingWidgetMixin):
    parent_r_pad = NumericProperty()
    is_codespan = BooleanProperty(False)
    open_bbcode_tag = StringProperty()

    def __init__(self, **kwargs):
        if kwargs.get("font_hinting") == "mono":
            kwargs.update({"highlight": True})
        super().__init__(**kwargs)
        self.fbind("parent", self.handle_parent)
        self.fbind("texture_size", self.handle_parent_height)

    def handle_parent(self, instance, value):
        self.parent.fbind("height", self.handle_parent_height)
        self.parent.fbind("padding", self.handle_parent_padding)
        return True

    def handle_parent_height(self, instance, value):
        parent = self.parent
        p_pad = parent.padding
        n_pads = len(p_pad)
        f_table = {
            4: lambda p: sum((p.padding[1], p.padding[3])),
            2: lambda p: p.padding[1],
            1: lambda p: p.padding,
        }
        vert_pad = f_table.get(n_pads, lambda p: 0)
        calc_height = max(self.height - vert_pad(parent), self.texture_size[1])
        self.height = calc_height

    def handle_parent_padding(self, instance, value):
        p_pad = self.parent.padding
        if len(p_pad) == 4:
            self.parent_r_pad = p_pad[2]
        elif len(p_pad) == 2:
            self.parent_r_pad = p_pad[0]
        elif len(p_pad) == 1:
            self.parent_r_pad = p_pad
        else:
            self.parent_r_pad = 0


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
