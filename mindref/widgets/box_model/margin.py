from kivy.properties import VariableListProperty, ColorProperty, AliasProperty
from kivy.uix.anchorlayout import AnchorLayout

from utils import import_kv

import_kv(__file__)


class MarginBox(AnchorLayout):
    """
    Outermost box
    Expands to fit, uses margins to force contents away from edge
    """

    box_margin: AliasProperty
    box_padding = VariableListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_margin(self):
        return self.padding

    def set_margin(self, val):
        self.padding = val

    box_margin = AliasProperty(get_margin, set_margin, bind=("padding",), cache=True)
