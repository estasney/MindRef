from __future__ import annotations

import abc
from typing import Protocol

from adapters.notes.note_repository import AbstractNoteRepository
from domain.editable import EditableNote
from domain.markdown_note import MarkdownNote


class AbstractEditorRepository(abc.ABC):
    @abc.abstractmethod
    def new_note(self, category: str, idx: int) -> EditableNote:
        ...

    @abc.abstractmethod
    def edit_note(self, note: MarkdownNote) -> EditableNote:
        ...

    @abc.abstractmethod
    def cancel_note(self, note: EditableNote):
        ...

    @abc.abstractmethod
    def edit_current_note(self, app: NoteServiceApp) -> EditableNote:
        ...


class NoteServiceApp(Protocol):
    note_service: "AbstractNoteRepository"
