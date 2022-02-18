import re

from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout

from utils import import_kv

import_kv(__file__)

table_re = re.compile(r"((?:=|-)+ +(?:=|-)+)")


class ContentRST(AnchorLayout):
    note_text = StringProperty()
    rst_doc = ObjectProperty()
    is_table = BooleanProperty(False)
    bg_color = StringProperty('#000000')
    paragraph_color = StringProperty('#ffffff')

    def __init__(self, content_data, **kwargs):
        super(ContentRST, self).__init__(**kwargs)
        self.note_text = content_data['text']
