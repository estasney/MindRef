from __future__ import annotations

from pathlib import Path
from typing import Generator, Optional, Union

from marko.block import BlankLine, Document, Heading
from marko.ext.gfm import gfm

from . import BackendProtocol
from ..domain import CodeNote, MarkdownNote, ShortcutNote, make_note


class FileSystemBackend(BackendProtocol):
    """
    Categories are defined in a single Markdown Document
    Individual notes are delimited by section
    """

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self._current_category = None
        self._note_cycler = None
        self.note_index = 0
        self.notes = None

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
    def categories(self) -> Generator[str]:
        for file in (f for f in self.storage_path.iterdir() if f.is_file()):
            file_valid, msg = self._note_path_valid(file, True)
            if not file_valid:
                raise Exception(msg)
            yield file.stem

    @property
    def current_category(self):
        return self._current_category

    @current_category.setter
    def current_category(self, value: Optional[str]):
        self._current_category = value
        if self._current_category:
            ...

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

    def parse_category_notes(self) -> list[Union[ShortcutNote, CodeNote, MarkdownNote]]:
        notes = []
        for file in self.storage_path.iterdir():
            file_valid, msg = self._note_path_valid(file, True)
            if not file_valid:
                raise Exception(msg)
            with file.open(mode="r", encoding="utf-8") as note_doc:
                note_text = note_doc.read()
            md_doc = gfm.parse(note_text)
            for idx, note in enumerate(self._note_generator(md_doc)):
                notes.append(make_note(idx=idx, category=file.stem, blocks=note))
        return notes

    def next_note(self):
        ...

    def previous_note(self):
        pass
