from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mindref.lib.domain.markdown_note import MarkdownNote


@dataclass
class EditableNote:
    category: str
    idx: int
    md_note: MarkdownNote | None
    edit_title: str = field(default="")
    edit_text: str = field(default="")

    def __repr__(self):
        attrs = ("category", "idx", "edit_title")
        return f"{type(self).__name__}({','.join(f'{p}={getattr(self, p)}' for p in attrs)})"

    @classmethod
    def from_markdown_note(cls, note: MarkdownNote):
        return EditableNote(
            category=note.category,
            idx=note.idx,
            md_note=note,
            edit_text=note.text,
            edit_title=note.filepath.stem,
        )
