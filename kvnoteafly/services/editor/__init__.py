import abc
from dataclasses import field, dataclass

from services.domain import MarkdownNote
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from services.backend import BackendProtocol
    from kivy.app import App


class NoteServiceApp(Protocol):
    note_service: "BackendProtocol"


@dataclass
class EditableNote:
    note: MarkdownNote
    edit_text: str = field(init=False)

    def save(self, editor: "EditorProtocol"):
        """Convert to MarkdownNote"""
        return editor.save_note(self)

    @classmethod
    def open(cls, note: MarkdownNote):
        """Wrap a note with Editable Note"""
        return EditableNote(note=note)

    def __post_init__(self):
        self.edit_text = self.note.text


class EditorProtocol(abc.ABC):
    @abc.abstractmethod
    def new_note(self) -> EditableNote:
        ...

    @abc.abstractmethod
    def edit_note(self, note: MarkdownNote) -> EditableNote:
        ...

    @abc.abstractmethod
    def edit_current_note(self, app: NoteServiceApp) -> EditableNote:
        ...

    @abc.abstractmethod
    def save_note(self, note: EditableNote) -> MarkdownNote:
        ...
