from __future__ import annotations

from adapters.editor.editor_repository import (
    AbstractEditorRepository,
)
from domain.editable import EditableNote
from domain.markdown_note import MarkdownNote


class FileSystemEditor(AbstractEditorRepository):
    def __init__(self, get_app):
        super().__init__(get_app)

    def new_note(self, category: str, idx: int) -> EditableNote:
        """
        Get an editable note from empty source
        """
        data_note = EditableNote(category=category, idx=idx, md_note=None)
        return data_note

    def edit_note(self, note: MarkdownNote) -> EditableNote:
        """
        Get an editable note from an existing MarkdownNote
        """
        data_note = EditableNote.from_markdown_note(note=note)
        return data_note

    def cancel_note(self, note: EditableNote):
        """
        Canceled note editing

        Parameters
        ----------
        note

        Returns
        -------

        """
        ...

    def edit_current_note(self) -> EditableNote:
        current = self.get_app().note_service.get_current_note(on_complete=None)
        return self.edit_note(current)
