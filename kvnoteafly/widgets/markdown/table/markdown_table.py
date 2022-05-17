from typing import Union, TYPE_CHECKING

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.text import Label as LabelCore

from utils import import_kv

import_kv(__file__)

if TYPE_CHECKING:
    from services.domain.md_parser_types import MdTableHeadCell, MdTableBodyCell


class MarkdownTable(GridLayout):
    pass


class MarkdownCellLabel(Label):
    row = ObjectProperty()
    x_extent = NumericProperty()
    y_extent = NumericProperty()
    extents = ReferenceListProperty(x_extent, y_extent)

    parent_r_pad = NumericProperty()
    _parent_vert_pad_func = None

    def __init__(self, **kwargs):
        super(MarkdownCellLabel, self).__init__(**kwargs)
        if kwargs.get("font_hinting") == "mono":
            self.enable_mono_feature()

    def on_parent(self, instance, value):
        self.row = value
        self.row.fbind("height", self.parent_height)
        self.parent_r_pad = self.get_parent_r_pad(self.row)

    def get_parent_r_pad(self, parent):
        p_pad = parent.padding
        if len(p_pad) == 4:
            return p_pad[2]
        elif len(p_pad) == 2:
            return p_pad[0]
        elif len(p_pad) == 1:
            return p_pad
        else:
            return 0

    def parent_vert_pad_func(self, parent):
        if self._parent_vert_pad_func:
            return self._parent_vert_pad_func(parent)
        p_pad = parent.padding
        if len(p_pad) == 4:
            self._parent_vert_pad_func = lambda p: sum((p.padding[1], p.padding[3]))
        elif len(p_pad) == 2:
            self._parent_vert_pad_func = lambda p: p.padding[1]
        elif len(p_pad) == 1:
            self._parent_vert_pad_func = lambda p: p.padding
        else:
            self._parent_vert_pad_func = lambda p: 0
        return self._parent_vert_pad_func(parent)

    def parent_height(self, parent, height):
        self.height = max(
            height - self.parent_vert_pad_func(parent), self.texture_size[1]
        )

    def enable_mono_feature(self):
        # List for texture to be created. Then we get the x, y extent
        self.bind(texture=self.get_extents)

    def get_extents(self, instance, value):
        # Texture created
        w, h = self._label.get_extents(self.text)

        # Now we can draw our codespan background
        self.x_extent = w + (2 * self.padding_x)
        self.y_extent = h + self.padding_y

        Clock.schedule_once(self.draw_codespan_extents)

    def get_x(self):
        if self.halign == "left":
            return self.center_x - self.texture_size[0] * 0.5
        elif self.halign == "center":
            return self.center_x - self.x_extent * 0.5
        elif self.halign == "right":
            return self.texture_size[0] - self.x_extent + (4 * self.padding_x)
        else:
            return self.center_x

    def get_y(self):
        return (self.center_y - self.texture_size[1] * 0.5) + (self.padding_y * 0.5)

    def draw_codespan_extents(self, *args, **kwargs):
        with self.canvas.before:
            Color(*App.get_running_app().colors["Gray"], 1)
            Rectangle(pos=(self.get_x(), self.get_y()), size=self.extents)


class MarkdownRow(BoxLayout):
    is_head = BooleanProperty()
