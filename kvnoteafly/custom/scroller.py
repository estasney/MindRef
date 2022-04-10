from typing import List

from kivy.core.window import Window
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    NumericProperty,
    ListProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from custom.keyboard import KeyboardImage
from db import NoteType
from utils import import_kv

import_kv(__file__)


class ScrollingListView(ScrollView):
    child_object = ObjectProperty()

    def set(self, notes: List[dict], *args, **kwargs):
        if not self.children:
            layout = ListView(cols=1, size_hint=(None, None), width=Window.width)
            layout.bind(minimum_height=layout.setter("height"))
            self.add_widget(layout)
            self.child_object = layout
        self.children[0].set(notes)


class ListItem(GridLayout):
    title_text = StringProperty()
    index = NumericProperty()

    def __init__(self, content_data: dict, *args, **kwargs):
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
        super().__init__(**kwargs)


class ListItemKeyboard(GridLayout):
    title_text = StringProperty()
    index = NumericProperty()
    keyboard_buttons = ListProperty()
    keyboard_container = ObjectProperty()

    def __init__(self, content_data: dict, **kwargs):
        self.title_text = content_data["title"]
        self.index = content_data["idx"]
        self.keyboard_buttons = content_data["keys_str"].split(",")
        super().__init__(**kwargs)
        self.keyboard_container.set(self.keyboard_buttons)


class ListItemKeyboardContainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set(self, btns: List[str]):
        for btn in btns:
            kbd_widget = KeyboardImage(text=btn, size_hint_x=1)
            self.add_widget(kbd_widget)


class ListView(GridLayout):
    def set(self, notes: List[dict]):
        self.clear_widgets()
        for note in notes:

            if note["note_type"] == NoteType.KEYBOARD_NOTE.name:
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
