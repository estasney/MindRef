from __future__ import annotations

import abc

from domain.protocols import AppRegistryProtocol, GetApp
from adapters.notes.note_repository import AbstractNoteRepository
from domain.editable import EditableNote
from domain.markdown_note import MarkdownNote


class NoteServiceAppProtocol(AppRegistryProtocol):
    """
    Protocol that defines an App with a Registry and note_service
    """

    note_service: "AbstractNoteRepository"


class AbstractEditorRepository(abc.ABC):
    def __init__(self, get_app: GetApp[NoteServiceAppProtocol]):
        """

        Parameters
        ----------
        get_app : Callable
            Callable that returns an object implementing `NoteServiceAppProtocol`
        """
        self.get_app = get_app

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
    def edit_current_note(self) -> EditableNote:
        ...