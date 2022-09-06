from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv

import_kv(__file__)


class TypeAhead(BoxLayout):
    """
    Container for TypeAhead Widget
    """

    typer = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
