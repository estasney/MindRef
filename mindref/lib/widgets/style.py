from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from lib.utils import import_kv

import_kv(__file__)


class BaseLabel(Label):
    ...


class XSmallLabel(BaseLabel):
    ...


class SmallLabel(BaseLabel):
    ...


class LargeLabel(BaseLabel):
    ...


class XLargeLabel(BaseLabel):
    ...


class ExpandingLabel(BaseLabel):
    ...


class TitleInput(TextInput):
    ...


class IconLabel(BaseLabel):
    icon_code = StringProperty()
