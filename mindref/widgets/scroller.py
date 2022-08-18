from typing import Sequence, TYPE_CHECKING

from kivy.core.window import Window
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from widgets.keyboard import KeyboardImage
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


class ListItemKeyboard(GridLayout):
    title_text = StringProperty()
    index = NumericProperty()
    keyboard_buttons = ListProperty()
    keyboard_container = ObjectProperty()

    def __init__(self, content_data: "MarkdownNoteDict", **kwargs):
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
        self.keyboard_buttons = content_data["shortcut_keys"]
        super().__init__(**kwargs)
        self.keyboard_container.set(self.keyboard_buttons)


class ListItemKeyboardContainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set(self, btns: list[str]):
        for btn in btns:
            kbd_widget = KeyboardImage(text=btn, size_hint_x=1)
            self.add_widget(kbd_widget)


class ListView(GridLayout):
    def set(self, meta_notes: Sequence["MarkdownNoteDict"]):
        self.clear_widgets()

        for note in meta_notes:
            if note["has_shortcut"]:
                self.add_widget(
                    ListItemKeyboard(
                        content_data=note,
                        width=Window.width,
                        height=(Window.height / 6),
                        size_hint=(None, None),
                    )
                )
            else:
                self.add_widget(
                    ListItem(
                        content_data=note,
                        width=Window.width,
                        height=(Window.height / 6),
                        size_hint=(None, None),
                    )
                )
