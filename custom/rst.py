from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.anchorlayout import AnchorLayout

from utils import import_kv
import re

import_kv(__file__)


table_re = re.compile(r"((?:=|-)+ +(?:=|-)+)")

class ContentRST(AnchorLayout):
    note_text = StringProperty()
    is_table = BooleanProperty(False)
    para_color = StringProperty('000000')

    def __init__(self, content_data, **kwargs):
        self.note_text = content_data['text']
        if table_re.findall(self.note_text):
            self.is_table = True
            self.para_color = 'ffffff'
        super(ContentRST, self).__init__(**kwargs)
