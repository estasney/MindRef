from typing import TYPE_CHECKING

from kivy import Logger
from kivy.clock import Clock
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

from mindref.lib.utils import fmt_items, import_kv, sch_cb, schedulable

if TYPE_CHECKING:
    from mindref.lib.domain.markdown_note import MarkdownNoteDict

import_kv(__file__)


class ScrollingListView(ScrollView):
    content = ObjectProperty()


class ListView(GridLayout):
    meta_notes = ListProperty()
    pending_items = ListProperty()
    """
    Attributes
    ----------
    meta_notes : ListProperty
        Reflects App's note_meta
    pending_items : ListProperty
        Works a queue. When self.add_item_trigger is called, we process one at a time until returning False
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_item_trigger = Clock.create_trigger(
            self.add_item, timeout=0.01, interval=True
        )

    def add_item(self, *_args):
        if self.pending_items:
            note_data = self.pending_items.pop()
            widget = ListItem(content_data=note_data)
            self.add_widget(widget)
            Logger.debug(
                f"{type(self).__name__}: add_item - {fmt_items(note_data, 'title', 'idx')}"
            )
            return None
        Logger.info(f"{type(self).__name__}: add_item - complete - cancel trigger")
        return False

    def on_meta_notes(self, _, value: list["MarkdownNoteDict"]):
        Logger.info(f"{type(self).__name__} : on_meta_notes : {len(value)} items")
        clear_widgets = schedulable(self.clear_widgets)
        startup_timer = schedulable(self.add_item_trigger)
        self.pending_items = []
        if value:
            self.pending_items = value[::-1]
            sch_cb(clear_widgets, startup_timer, timeout=0.05)
        else:
            sch_cb(clear_widgets)
            if self.add_item_trigger.is_triggered:
                self.add_item_trigger.cancel()


class ListItem(ButtonBehavior, BoxLayout):
    title_text = StringProperty()
    index = NumericProperty()

    def __init__(self, content_data: "MarkdownNoteDict", **kwargs):
        super().__init__(**kwargs)
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
