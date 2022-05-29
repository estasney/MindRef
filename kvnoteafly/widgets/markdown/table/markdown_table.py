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

from widgets.behavior import LabelHighlight

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
        self._parent_vert_pad_func = None

    def on_parent(self, instance, value):
        self.parent.bind(height=self.parent_height)
        self.parent_r_pad = self.get_parent_r_pad(self.parent)

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


class MarkdownRow(BoxLayout):
    ...

    def on_children(self, instance, value):
        Clock.schedule_once(self.draw_cell_border)
        return True

    def draw_cell_border(self, dt):
        with self.canvas:
            Color(rgba=App.get_running_app().colors["Dark"])
            for child in self.children[:-1]:
                Line(width=1.2, rectangle=(self.x, self.y, child.width, self.height))

    # def on_pos(self, instance, value):
    #     with self.canvas.before:
    #         self.canvas.before.clear()
    #         Color(rgba=App.get_running_app().colors['Dark'])
    #         Line(width=1.2, rectangle=(self.x, self.y, self.width, self.height))


# """canvas:
#         Color:
#             rgba: app.colors['Dark']
#         Line:
#             width: 1.2
#             rectangle: self.x, self.y, self.width, self.height
# """
