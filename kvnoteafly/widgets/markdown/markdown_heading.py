from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.label import Label

from utils import import_kv

import_kv(__file__)


class MarkdownHeading(Label):

    document = ObjectProperty(None)
    level = NumericProperty(None)
    content = StringProperty(None)

    def __init__(self, document, level, content, *args, **kwargs):
        self.document = document
        self.level = level
        self.content = content
        self.text = content
        super().__init__(*args, **kwargs)
