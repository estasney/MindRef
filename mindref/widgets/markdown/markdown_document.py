from typing import TYPE_CHECKING

from kivy.properties import (
    ObjectProperty,
    StringProperty,
)
from kivy.uix.scrollview import ScrollView

from utils import import_kv
from widgets.markdown.markdown_widget_parser import MarkdownWidgetParser

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNoteDict

import_kv(__file__)


class MarkdownDocument(ScrollView):
    text = StringProperty()
    title = StringProperty()
    document = ObjectProperty()
    content = ObjectProperty()

    def __init__(self, content_data: dict, **kwargs):
        super(MarkdownDocument, self).__init__(**kwargs)
        self.document = content_data["document"]
        self.text = content_data["text"]
        self.title = content_data["title"]
        self.current = None
        self.current_params = None
        self.do_scroll_x = False
        self.do_scroll_y = True

    def on_document(self, _, _value: "MarkdownNoteDict"):
        self.content.clear_widgets()
        for child in self.document:
            parser = MarkdownWidgetParser()
            child_result = parser.parse(child)
            if child_result:
                self.content.add_widget(child_result)

    def render(self):
        self._load_from_text()
