from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Optional, TYPE_CHECKING

from marko.ext.gfm import gfm

from . import BackendProtocol, NoteIndex
from ..domain import MarkdownNote

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    NotesMapping = Mapping[str, list[Path]]


class FileSystemBackend(BackendProtocol):
    _notes: Optional["NotesMapping"]
    _index: Optional[NoteIndex]
    _current_category: Optional[str]
    storage_path: Path

    """
    Categories are defined with directories
    Individual notes defined as markdown files within their respective categories
    """

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self._current_category = None
        self._notes = None
        self._index = None
        self._discover_notes()

    def _discover_notes(self):
        categories, folders = zip(*[(f.name, f) for f in self.storage_path.iterdir() if f.is_dir()])
        notes = defaultdict(lambda: list())
        for folder in folders:
            notes[folder.name] = [f for f in folder.iterdir() if f.is_file()]
        self._notes = notes

    @property
    def notes(self) -> "NotesMapping":
        if not self._notes:
            self._discover_notes()
        return self._notes

    @property
    def categories(self) -> list[str]:
        return list(self.notes.keys())

    @property
    def current_category(self) -> Optional[str]:
        return self._current_category

    @current_category.setter
    def current_category(self, value: Optional[str]):
        if not value:
            self._current_category = None
            self._index = None
            return
        if value not in self.categories:
            raise KeyError(f"{value} not found in Categories")
        self._current_category = value
        self._index = NoteIndex(size=len(self.notes[value]))

    def set_index(self, n: int):
        if not self._index:
            raise Exception("No Index")
        self._index.set_current(n)

    def read_note(self, category=None, index=None) -> MarkdownNote:
        category = category if category else self.current_category
        index = index if index is not None else self._index.current
        note_file = self.notes[category][index]
        with open(note_file, mode="r", encoding="utf-8") as fp:
            note_text = fp.read()
        md_doc = gfm.parse(note_text)
        return MarkdownNote(text=note_text, category=category, idx=index, document=md_doc, file=note_file)

    def next_note(self) -> MarkdownNote:
        if not self._index:
            raise Exception(f"No Index")
        self._index.next()
        return self.read_note()

    def previous_note(self) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        self._index.previous()
        return self.read_note()

    def current_note(self) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        return self.read_note()
