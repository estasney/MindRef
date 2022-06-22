from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from utils import import_kv

import_kv(__file__)


class BaseLabel(Label):
    ...


class SmallLabel(Label):
    ...


class LargeLabel(Label):
    ...


class TitleInput(TextInput):
    ...
