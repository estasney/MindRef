from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from custom.code import ContentCode
from custom.keyboard import ContentKeyboard
from custom.markdown.markdown_document import MarkdownDocument
from custom.rst import ContentRST
from db import NoteType
from utils import import_kv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kvnoteafly.services.domain import NotesDict

import_kv(__file__)


class Note(BoxLayout):
    note_title = ObjectProperty()
    note_content = ObjectProperty()
    note_tags = ObjectProperty()

    def set_note_content(self, note_data: dict):
        title_data = {"title": note_data["title"]}

        content_data = {
            "text": note_data["text"],
            "document": note_data["document"],
            "title": note_data["title"],
        }

        self.note_title.set(title_data)
        self.note_content.set(content_data)


class NoteContent(BoxLayout):
    def set(self, content_data: "NotesDict"):

        self.clear_widgets()
        self._set_markdown(content_data)

    def _set_text(self, content_data: dict):
        self.add_widget(ContentRST(content_data=content_data))

    def _set_keyboard(self, content_data: dict):
        self.add_widget(ContentKeyboard(content_data=content_data))

    def _set_code(self, content_data: dict):
        self.add_widget(ContentCode(content_data=content_data))

    def _set_markdown(self, content_data: dict):
        self.add_widget(MarkdownDocument(content_data=content_data))


class NoteTitle(BoxLayout):
    title_text = StringProperty()
    play_state = StringProperty()
    button_bar = ObjectProperty()
    play_state_button = ObjectProperty()

    def __init__(self, **kwargs):
        if "note_title" in kwargs:
            self.title_text = kwargs.pop("note_title")
        super().__init__(**kwargs)

    def set(self, title_data):
        self.title_text = title_data["title"]

    def on_play_state(self, instance, value):
        pass


class NoteTags(BoxLayout):
    pass
