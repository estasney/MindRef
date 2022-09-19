from typing import Optional

from kivy.properties import ObjectProperty

from domain.markdown_note import MarkdownNoteDict
from utils import import_kv
from widgets.note import Note
from widgets.screens import InteractScreen

import_kv(__file__)


class NoteCategoryScreen(InteractScreen):
    current_note: "Note" = ObjectProperty()

    def set_note_content(self, note_data: Optional["MarkdownNoteDict"]):
        if note_data:
            self.current_note.set_note_content(note_data)
        else:
            self.current_note.clear_note_content()
