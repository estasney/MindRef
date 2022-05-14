from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from utils import import_kv

import_kv(__file__)


class MarkdownTable(GridLayout):
    pass


class MarkdownCell(GridLayout):
    is_head = BooleanProperty(False)
    align = StringProperty("center")

    def __init__(self, align, **kwargs):
        super().__init__(**kwargs)
        if align:
            self.align = align

    def on_parent(self, instance, parent):
        self.is_head = parent.is_head


class MarkdownCellContent(Label):

    mx = NumericProperty(10)
    my = NumericProperty(10)
    document = ObjectProperty(None)
    bold = BooleanProperty(False)
    text = StringProperty()
    align = StringProperty("center")

    def on_parent(self, instance, parent):
        self.bold = parent.is_head
        self.align = parent.align


class MarkdownRow(BoxLayout):
    is_head = BooleanProperty()
