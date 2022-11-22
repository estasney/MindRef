from functools import partial

from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from utils import import_kv, sch_cb
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNoteDict


import_kv(__file__)


class ScrollingListView(ScrollView):
    meta_notes = ListProperty()
    content = ObjectProperty()


class ListView(GridLayout):
    meta_notes = ListProperty()

    def add_item(self, *_args, **kwargs):
        note_data = kwargs.get("note_data")
        widget = ListItem(content_data=note_data)
        self.add_widget(widget)

    def on_meta_notes(self, instance, value):
        clear = lambda dt: self.clear_widgets()
        add_widgets = [
            partial(self.add_item, note_data=note) for note in self.meta_notes
        ]
        sch_cb(clear, *add_widgets, timeout=0.1)


class ListItem(ButtonBehavior, BoxLayout):
    title_text = StringProperty()
    index = NumericProperty()

    def __init__(self, content_data: "MarkdownNoteDict", *args, **kwargs):
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
        super().__init__(**kwargs)
