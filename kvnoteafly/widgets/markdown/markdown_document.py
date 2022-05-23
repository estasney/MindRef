from typing import TYPE_CHECKING

from kivy.properties import (
    AliasProperty,
    DictProperty,
    Logger,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex, get_hex_from_color


from utils import import_kv
from widgets.markdown.markdown_visitor import MarkdownVisitor

if TYPE_CHECKING:
    from services.domain import MarkdownNoteDict

import_kv(__file__)


class MarkdownDocument(ScrollView, MarkdownVisitor):
    text = StringProperty()
    title = StringProperty()
    document = ObjectProperty()
    base_font_size = NumericProperty(31)
    content = ObjectProperty()
    scatter = ObjectProperty()

    def __init__(self, content_data: dict, **kwargs):
        super(MarkdownDocument, self).__init__(**kwargs)
        self.document = content_data["document"]
        self.text = content_data["text"]
        self.title = content_data["title"]
        self.current = None
        self.current_params = None
        self.do_scroll_x = False
        self.do_scroll_y = True

    def on_document(self, instance, value: "MarkdownNoteDict"):
        self.content.clear_widgets()
        for child in self.document:
            if self.visit(child):
                child_result = self.pop_entry()
                self.content.add_widget(child_result)

    def render(self):
        self._load_from_text()
