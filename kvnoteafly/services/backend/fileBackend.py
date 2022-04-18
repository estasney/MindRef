from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Mapping, Optional, TYPE_CHECKING, Union

from marko.block import BlankLine, Document, Heading
from marko.ext.gfm import gfm

from . import BackendProtocol, NoteIndex
from ..domain import make_note

if TYPE_CHECKING:
    from ..domain import NotesDict

    NotesMapping = Mapping[str, list[NotesDict]]


class FileSystemBackend(BackendProtocol):
    _notes: Optional["NotesMapping"]
    _index: Optional[NoteIndex]
    _current_category: Optional[str]
    storage_path: Path

    """
    Categories are defined in a single Markdown Document
    Individual notes are delimited by section
    """

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self._current_category = None
        self._notes = None
        self._index = None
        self._discover_notes()

    def _discover_notes(self):
        notes = defaultdict(lambda: list())
        for file in self.storage_path.iterdir():
            file_valid, msg = self._note_path_valid(file, True)
            if not file_valid:
                raise Exception(msg)
            with file.open(mode="r", encoding="utf-8") as note_doc:
                note_text = note_doc.read()
            md_doc = gfm.parse(note_text)
            for idx, note in enumerate(self._note_generator(md_doc)):
                notes[file.stem].append(
                    make_note(idx=idx, category=file.stem, blocks=note).to_dict()
                )
        self._notes = notes

    @property
    def notes(self) -> "NotesMapping":
        if not self._notes:
            self._discover_notes()
        return self._notes

    @classmethod
    def _note_path_valid(cls, fp: Path, existing: bool) -> tuple[bool, Optional[str]]:
        if fp.suffix.lower() == ".md":
            if existing:
                if fp.is_file():
                    return True, None
                return False, f"{fp} does not exist"
            return True, None
        return False, f"{fp} has unsupported suffix : {fp.suffix}"

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

    @classmethod
    def _note_generator(cls, doc: Document):
        """Heading indicates start of new note. Yield Heading and everything else up to another Heading"""
        store = []
        for child in doc.children:
            if isinstance(child, Heading):
                if store:
                    yield store
                    store.clear()
                else:
                    store.append(child)
            if isinstance(child, BlankLine):
                continue
            store.append(child)
        if store:
            yield store

    def set_index(self, n: int):
        if not self._index:
            raise Exception("No Index")
        self._index.set_current(n)

    def parse_category_notes(self) -> list[NotesDict]:
        notes = []
        for file in self.storage_path.iterdir():
            file_valid, msg = self._note_path_valid(file, True)
            if not file_valid:
                raise Exception(msg)
            with file.open(mode="r", encoding="utf-8") as note_doc:
                note_text = note_doc.read()
            md_doc = gfm.parse(note_text)
            for idx, note in enumerate(self._note_generator(md_doc)):
                notes.append(
                    make_note(idx=idx, category=file.stem, blocks=note).to_dict()
                )
        return notes

    def next_note(self) -> NotesDict:
        if not self._index:
            raise Exception(f"No Index")
        self._index.next()
        return self.notes[self.current_category][self._index.current]

    def previous_note(self) -> NotesDict:
        if not self._index:
            raise Exception("No Index")
        self._index.previous()
        return self.notes[self.current_category][self._index.current]

    def current_note(self) -> NotesDict:
        if not self._index:
            raise Exception("No Index")
        return self.notes[self.current_category][self._index.current]
