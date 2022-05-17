from kivy.uix.gridlayout import GridLayout

from utils import import_kv

import_kv(__file__)


class MarkdownList(GridLayout):
    def __init__(self, **kwargs):
        super(MarkdownList, self).__init__(**kwargs)
