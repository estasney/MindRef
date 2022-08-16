from copy import deepcopy
from typing import TYPE_CHECKING

from kivy import Logger
from kivy.cache import Cache
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv, sch_cb
from utils.caching import cache_key_note, kivy_cache

import_kv(__file__)

from widgets.keyboard import ContentKeyboard
from widgets.markdown.markdown_document import MarkdownDocument

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNoteDict

Cache.register("note_widget", limit=10, timeout=3600)


@kivy_cache(cache_name="note_widget", key_func=cache_key_note)
def get_cached_note(*, content_data: "MarkdownNoteDict", parent: "NoteContent"):
    if content_data.get("has_shortcut", False):
        result = ContentKeyboard(content_data=content_data)
    else:
        result = MarkdownDocument(content_data=content_data)
    return result


class Note(BoxLayout):
    note_title = ObjectProperty()
    note_content = ObjectProperty()
    note_tags = ObjectProperty()

    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)

    def set_note_content(self, note_data: "MarkdownNoteDict"):

        title = note_data["title"]
        set_title = lambda x: self.note_title.set({"title": title})
        data = deepcopy(note_data)
        set_content = lambda x: self.note_content.set(data)
        sch_cb(0, set_title, set_content)

    def clear_note_content(self):
        clear_title = lambda x: self.note_title.set({"title": ""})
        self.note_title.set({"title": ""})
        clear_content = lambda x: self.note_content.clear()
        sch_cb(0, clear_title, clear_content)


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

    def clear(self):
        self.clear_widgets()

    def _set_keyboard(self, content_data: "MarkdownNoteDict"):
        widget = get_cached_note(content_data=content_data, parent=self)
        self.add_widget(widget)

    def _set_markdown(self, content_data: "MarkdownNoteDict"):
        md_widget = get_cached_note(content_data=content_data, parent=self)
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
