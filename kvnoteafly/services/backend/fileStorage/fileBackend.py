from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional, cast

from marko.ext.gfm import gfm

from services.backend import BackendProtocol, NoteIndex
from services.backend.fileStorage.utils import CategoryFiles, CategoryNoteMeta, _get_folder_files, _load_category_metas
from services.backend.utils import LazyLoaded
from services.domain import MarkdownNote, MarkdownNoteMeta


class FileSystemBackend(BackendProtocol):

    _index: Optional[NoteIndex]
    _current_category: Optional[str]
    storage_path: Path
    category_files: "CategoryFiles" = LazyLoaded()
    category_meta: "CategoryNoteMeta" = LazyLoaded(default=list)

    """
    Categories are defined with directories
    Individual notes defined as markdown files within their respective categories
    """

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self._category_files = None
        self._category_meta = []
        self._current_category = None
        self._index = None

    @category_files
    def _discover_notes(self):
        """
        Read `self.storage_path` looking for children folders and the associated notes within each

        Notes
        -----
        Does not read the notes, only gathers a listing of them
        """
        note_files = asyncio.run(_get_folder_files(self.storage_path))
        return note_files

    @category_meta
    def _load_category_meta(self):
        category_files = self.category_files[self.current_category]
        meta_texts = asyncio.run(_load_category_metas(category_files))
        meta_texts = cast(list[tuple[int, str]], meta_texts)
        return [MarkdownNoteMeta(idx=i, text=text, file=f).to_dict() for i, text, f in meta_texts]

    @property
    def categories(self) -> list[str]:
        return list(self.category_files.keys())

    @property
    def current_category(self) -> Optional[str]:
        return self._current_category

    @current_category.setter
    def current_category(self, value: Optional[str]):
        if not value:
            self._current_category = None
            self._index = None
            self.category_meta = []
            return
        if value not in self.categories:
            raise KeyError(f"{value} not found in Categories")
        self._current_category = value
        self._load_category_meta()
        self._index = NoteIndex(size=len(self.category_files[value]))

    def set_index(self, n: int):
        if not self._index:
            raise Exception("No Index")
        self._index.set_current(n)

    def read_note(self, category=None, index=None) -> MarkdownNote:
        category = category if category else self.current_category
        index = index if index is not None else self._index.current
        note_file = self.category_files[category][index]
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
