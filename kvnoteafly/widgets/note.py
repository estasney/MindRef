from typing import TYPE_CHECKING

from kivy import Logger
from kivy.cache import Cache
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv

import_kv(__file__)

from widgets.keyboard import ContentKeyboard
from widgets.markdown.markdown_document import MarkdownDocument

if TYPE_CHECKING:
    from kvnoteafly.services.domain import MarkdownNoteDict

Cache.register("note_widget", limit=100, timeout=3600)


def get_cached_note(content_data: "MarkdownNoteDict"):
    key = f"{content_data['file']}-{content_data['idx']}-{content_data['text']}"
    cached_instance = Cache.get("note_widget", key)
    if cached_instance:
        if cached_instance.parent:
            cached_instance.parent.clear_widgets()
            Cache.append("note_widget", key, cached_instance)
        return cached_instance
    if content_data.get("has_shortcut", False):
        result = ContentKeyboard(content_data=content_data)
    else:
        result = MarkdownDocument(content_data=content_data)
    Cache.append("note_widget", key, result)
    return result


class Note(BoxLayout):
    note_title = ObjectProperty()
    note_content = ObjectProperty()
    note_tags = ObjectProperty()

    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)

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
        widget = get_cached_note(content_data)
        self.add_widget(widget)

    def _set_markdown(self, content_data: "MarkdownNoteDict"):
        md_widget = get_cached_note(content_data)
        self.add_widget(md_widget)


class NoteTitle(BoxLayout):
    title_text = StringProperty()
    edit_button = ObjectProperty()

    def __init__(self, **kwargs):
        if "note_title" in kwargs:
            self.title_text = kwargs.pop("note_title")
        super().__init__(**kwargs)

    def set(self, title_data):
        self.title_text = title_data["title"]

    def handle_edit(self):
        """Pass this to screen manager"""
        Logger.debug("Edit")
        self.parent.handle_edit()
        return True


class NoteTags(BoxLayout):
    pass
