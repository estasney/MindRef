from typing import Sequence, TYPE_CHECKING

from kivy.core.window import Window
from kivy.properties import (
    NumericProperty,
    StringProperty,
)
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from utils import import_kv

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNoteDict

import_kv(__file__)


class ScrollingListView(ScrollView):
    ...


class ListItem(GridLayout):
    title_text = StringProperty()
    index = NumericProperty()

    def __init__(self, content_data: "MarkdownNoteDict", *args, **kwargs):
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
        super().__init__(**kwargs)


class ListView(GridLayout):
    def set(self, meta_notes: Sequence["MarkdownNoteDict"]):
        self.clear_widgets()

        for note in meta_notes:
            self.add_widget(
                ListItem(
                    content_data=note,
                    width=Window.width,
                    height=(Window.height / 6),
                    size_hint=(None, None),
                )
            )
