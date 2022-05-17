from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from utils import import_kv

import_kv(__file__)


class MarkdownBlockQuote(GridLayout):
    text_content = StringProperty()
    content = ObjectProperty()

    def __init__(self, **kwargs):
        super(MarkdownBlockQuote, self).__init__(**kwargs)
