from typing import TYPE_CHECKING

from utils import import_kv

import_kv(__file__)

from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from widgets.behavior import LabelHighlight


if TYPE_CHECKING:
    pass


class MarkdownTable(GridLayout):
    pass


class MarkdownCellLabel(LabelHighlight):
    parent_r_pad = NumericProperty()
    _parent_vert_pad_func = None

    def __init__(self, **kwargs):
        if kwargs.get("font_hinting") == "mono":
            kwargs.update({"highlight": True})
        super(MarkdownCellLabel, self).__init__(**kwargs)

    def on_parent(self, instance, value):
        self.parent.fbind("height", self.parent_height)
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
    is_head = BooleanProperty()
