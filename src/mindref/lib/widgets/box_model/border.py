from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout

from mindref.lib.utils import import_kv

import_kv(__file__)


class BorderBox(AnchorLayout):
    """Offset from margin and displays a border"""

    border_size = NumericProperty(10)
    border_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
