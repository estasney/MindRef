from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from typing import TYPE_CHECKING
from utils import import_kv
from pygments.lexers import get_lexer_by_name

if TYPE_CHECKING:
    from kvnoteafly.services.domain import CodeNoteDict

import_kv(__file__)


class ContentCode(AnchorLayout):
    note_text = StringProperty()
    code_lexer = ObjectProperty()

    def __init__(self, content_data: "CodeNoteDict", **kwargs):
        self.note_text = content_data["text"]
        self.code_lexer = get_lexer_by_name(content_data["lexer"])
        super(ContentCode, self).__init__(**kwargs)
