from kivy.uix.gridlayout import GridLayout

from mindref.lib.utils import import_kv

import_kv(__file__)


class MarkdownList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
