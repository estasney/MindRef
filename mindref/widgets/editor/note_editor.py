from typing import TYPE_CHECKING

from kivy.properties import (
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from pygments.lexers import get_lexer_by_name

from utils import import_kv, attrsetter, sch_cb

import_kv(__file__)

if TYPE_CHECKING:
    from kivy.uix.codeinput import CodeInput


class NoteEditor(BoxLayout):
    """
    Attributes
    -----------
    editor
    lexer
    style_name
    init_text: StringProperty
    mode
    title_widget: ObjectProperty
        Text input which is only displayed when in mode 'add'
    """

    editor = ObjectProperty()
    lexer = ObjectProperty(get_lexer_by_name("Markdown"))
    style_name = StringProperty("paraiso-dark")
    init_text = StringProperty()
    mode = OptionProperty("edit", options=["add", "edit"])
    title_widget = ObjectProperty()

    def __init__(self, **kwargs):
        super(NoteEditor, self).__init__(**kwargs)
        self.bind(init_text=self.handle_init_text)
        self.title_widget = NoteTitleInput(size_hint_y=0.1, pos_hint={"top": 0})
        self.register_event_type("on_save")
        self.register_event_type("on_cancel")

    def handle_init_text(self, *_args):
        editor: "CodeInput" = self.editor
        editor.text = self.init_text

    def on_mode(self, *_args):

        if self.mode == "add":
            self.add_widget(self.title_widget, len(self.children))
        else:
            self.title_widget.input_widget.text = ""
            self.remove_widget(self.title_widget)

    def handle_press_save(self, *_args):
        if self.mode == "add":
            self.dispatch(
                "on_save",
                **{"text": self.editor.text, "title": self.title_widget.title},
            )
            clear_text = attrsetter(self.editor, "text", "")
            clear_title = attrsetter(self.title_widget.input_widget, "text", "")
            sch_cb(clear_text, clear_title, timeout=0.5)
        else:
            self.dispatch("on_save", **{"text": self.editor.text, "title": None})

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
