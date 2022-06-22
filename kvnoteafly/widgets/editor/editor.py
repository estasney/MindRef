from kivy import Logger
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from typing import TYPE_CHECKING

from kivy.uix.widget import Widget
from pygments.lexers import get_lexer_by_name

from utils import import_kv

import_kv(__file__)

if TYPE_CHECKING:
    from kivy.uix.codeinput import CodeInput


class NoteEditor(BoxLayout):
    editor = ObjectProperty()
    lexer = ObjectProperty(get_lexer_by_name("Markdown"))
    style_name = StringProperty("paraiso-dark")
    init_text = StringProperty()
    mode = OptionProperty("edit", options=["add", "edit"])
    title_widget = ObjectProperty()

    def __init__(self, **kwargs):
        super(NoteEditor, self).__init__(**kwargs)
        self.fbind("init_text", self.handle_init_text)
        self.fbind("mode", self.handle_mode_change)
        self.title_widget = NoteTitleInput(size_hint_y=0.1, pos_hint={"top": 0})
        self.register_event_type("on_save")
        self.register_event_type("on_cancel")

    def handle_init_text(self, instance, value):
        editor: "CodeInput" = self.editor
        editor.text = self.init_text

    def handle_mode_change(self, instance, value):
        if self.mode == "add":
            self.add_widget(self.title_widget, len(self.children))
        else:
            self.title_widget.input_widget.text = ""
            self.remove_widget(self.title_widget)

    def handle_press_save(self, *args, **kwargs):
        if self.mode == "add":
            self.dispatch(
                "on_save",
                **{"text": self.editor.text, "filename": self.title_widget.title}
            )
        else:
            self.dispatch("on_save", **{"text": self.editor.text})

    def on_save(self, *args, **kwargs):
        ...

    def on_cancel(self, *args, **kwargs):
        ...


class NoteTitleInput(BoxLayout):
    title = StringProperty()
    input_widget = ObjectProperty()

    def __init__(self, **kwargs):
        super(NoteTitleInput, self).__init__(**kwargs)
        self.input_widget.bind(text=self.setter("title"))
