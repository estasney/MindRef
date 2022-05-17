from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from utils import import_kv

import_kv(__file__)


class MarkdownHeading(Label):
    level = NumericProperty()


class MarkdownBlock(BoxLayout):
    ...
