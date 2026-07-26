from typing import TYPE_CHECKING

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
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

from mindref.lib.utils import sch_cb, schedulable

if TYPE_CHECKING:
    from mindref.lib.domain.markdown_note import MarkdownNoteDict

Builder.load_string("""
#:import LargeLabel mindref.lib.widgets.style
#:import BaseLabel mindref.lib.widgets.style
#:import FileButton mindref.lib.widgets.buttons
<ListView>:
    cols: 1
    height: self.minimum_height
    size_hint_y: None


<ScrollingListView>:
    do_scroll_x: False
    do_scroll_y: True
    content: content
    Scatter:
        size_hint_y: None
        height: content.minimum_height
        width: root.width
        scale: 1
        do_translation: False, False
        do_scale: False
        do_rotation: False
        ListView:
            meta_notes: app.note_category_meta
            size_hint_y: None
            id: content
            cols: 1
            height: self.minimum_height
            width: root.width

<ListItem>:
    padding: dp(5)
    canvas:
        Color:
            rgba: (*app.colors['Gray-400'][:3], 0.6)
        Line:
            width: dp(1.2)
            rectangle: (self.x, self.y, self.width, self.height)
        Color:
            rgba: app.colors['Primary'] if self.state == 'normal' else app.colors['Accent-One']
        Rectangle:
            size: self.size
            pos: self.pos
    orientation: 'horizontal'
    height: dp(40)
    size_hint_y: None
    size_hint_x: 1
    on_release: app.select_index(self.index)

    BaseLabel:
        text: root.title_text
        size_hint_x: 0.9
        size_hint_y: 1
        mipmap: True
        text_size: self.width, None
        font_size: sp(app.base_font_size)
        padding_x: dp(5)
        valign: 'middle'
        halign: 'left'
""")


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
