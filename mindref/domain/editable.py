from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNote


@dataclass
class EditableNote:
    category: str
    idx: int
    md_note: Optional["MarkdownNote"]
    edit_title: str = field(default="")
    edit_text: str = field(default="")

    @classmethod
    def from_markdown_note(cls, note: "MarkdownNote"):
        return EditableNote(
            category=note.category,
            idx=note.idx,
            md_note=note,
            edit_text=note.text,
            edit_title=note.filepath.stem,
        )
