from typing import TYPE_CHECKING

from kivy.properties import Logger, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv

import_kv(__file__)


from widgets.keyboard import ContentKeyboard
from widgets.markdown.markdown_document import MarkdownDocument

if TYPE_CHECKING:
    from kvnoteafly.services.domain import MarkdownNoteDict


class Note(BoxLayout):
    note_title = ObjectProperty()
    note_content = ObjectProperty()
    note_tags = ObjectProperty()

    def set_note_content(self, note_data: "MarkdownNoteDict"):
        self.note_title.set({"title": note_data["title"]})
        self.note_content.set(note_data)


class NoteContent(BoxLayout):
    def set(self, content_data: "MarkdownNoteDict"):
        self.clear_widgets()
        Logger.debug(
            f"NoteContent: {content_data['category']}, {content_data['title']}"
        )
        if content_data.get("has_shortcut", False):
            self._set_keyboard(content_data)
        else:
            self._set_markdown(content_data)

    def _set_keyboard(self, content_data: "MarkdownNoteDict"):
        self.add_widget(ContentKeyboard(content_data=content_data))

    def _set_markdown(self, content_data: "MarkdownNoteDict"):
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
