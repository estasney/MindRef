from typing import TYPE_CHECKING, Optional

from kivy.properties import ObjectProperty

from mindref.lib.utils import import_kv
from mindref.lib.widgets.screens.interactive import InteractScreen

if TYPE_CHECKING:
    from mindref.lib.domain.markdown_note import MarkdownNoteDict
    from mindref.lib.widgets.note import Note

import_kv(__file__)


class NoteCategoryScreen(InteractScreen):
    current_note: "Note" = ObjectProperty()

    def set_note_content(self, note_data: Optional["MarkdownNoteDict"]):
        self.current_note.set_note_content(note_data)
