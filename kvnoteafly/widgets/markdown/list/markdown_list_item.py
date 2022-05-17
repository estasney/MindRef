from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from utils import import_kv

import_kv(__file__)


class MarkdownListItem(GridLayout):

    text = StringProperty(None)
    content = ObjectProperty(None)
    level = NumericProperty(1)

    def __init__(self, text: str, level: int, **kwargs):
        super(MarkdownListItem, self).__init__(**kwargs)
        self.text = text
        self.level = level

    def on_text(self, instance, value):
        self.content.text = f"{self.level * ' '}{chr(8226)} {value}"
