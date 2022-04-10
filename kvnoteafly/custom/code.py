from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout

from utils import import_kv

import_kv(__file__)


class ContentCode(AnchorLayout):
    note_text = StringProperty()
    code_lexer = ObjectProperty()

    def __init__(self, content_data, **kwargs):
        self.note_text = content_data["text"]
        cl = content_data.get("code_lexer")
        if cl:
            self.code_lexer = content_data.get("code_lexer")
        super(ContentCode, self).__init__(**kwargs)
