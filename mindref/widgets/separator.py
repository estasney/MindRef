from kivy.properties import ColorProperty
from kivy.uix.widget import Widget

from utils import import_kv

import_kv(__file__)


class Separator(Widget):
    color = ColorProperty()
    ...


class HSeparator(Separator):
    ...


class VSeparator(Separator):
    ...
