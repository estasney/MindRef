from typing import TYPE_CHECKING

from kivy import Logger
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

from utils import caller, import_kv, sch_cb

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNoteDict

import_kv(__file__)


class ScrollingListView(ScrollView):
    content = ObjectProperty()


class ListView(GridLayout):
    meta_notes = ListProperty()

    def add_item(self, *_args, **kwargs):
        note_data = kwargs.get("note_data")
        widget = ListItem(content_data=note_data)
        self.add_widget(widget)

    def on_meta_notes(self, _, value: list["MarkdownNoteDict"]):
        Logger.info(f"{self.__class__.__name__} : on_meta_notes")
        clear_widgets = caller(self, "clear_widgets")
        add_widgets = [caller(self, "add_item", note_data=note) for note in value[::]]
        sch_cb(clear_widgets, *add_widgets, timeout=0.1)


class ListItem(ButtonBehavior, BoxLayout):
    title_text = StringProperty()
    index = NumericProperty()

    def __init__(self, content_data: "MarkdownNoteDict", **kwargs):
        super().__init__(**kwargs)
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
