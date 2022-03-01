from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from utils import import_kv

import_kv(__file__)


class MarkdownTable(GridLayout):
    pass


class MarkdownCell(GridLayout):
    pass


class MarkdownCellContent(Label):

    mx = NumericProperty(10)
    my = NumericProperty(10)
    document = ObjectProperty(None)
