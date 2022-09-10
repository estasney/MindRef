from kivy.properties import (
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from utils import import_kv

import_kv(__file__)


class ThemedButton(Button):
    ...


class HamburgerIcon(BoxLayout):
    release_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(HamburgerIcon, self).__init__(**kwargs)
