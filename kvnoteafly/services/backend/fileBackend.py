from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Optional, TYPE_CHECKING, cast
from operator import attrgetter, itemgetter

from marko.ext.gfm import gfm

from . import BackendProtocol, NoteIndex
from ..domain import MarkdownNote, MarkdownNoteDict, MarkdownNoteMeta, NoteMetaData

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    CategoryFiles = Mapping[str, list[Path]]
    CategoryNoteMeta = list["NoteMetaData"]

async def _fetch_fp_mtime(f: Path) -> tuple[Path, int]:
    return f, f.lstat().st_mtime_ns

async def _sort_fp_mtimes(files: list[Path]) -> list[Path]:
    """Fetch and sort file modified times"""
    fetched = await asyncio.gather(*[_fetch_fp_mtime(f) for f in files])
    fetched = sorted(fetched, key=itemgetter(1), reverse=True)
    return [f for f, _ in fetched]

async def _load_category_meta(i: int, note_path: Path) -> tuple[int, str, Path]:
    with note_path.open(mode="r", encoding="utf-8") as fp:
        note_text = fp.read()
    return i, note_text, note_path


async def _load_category_metas(note_paths: list[Path]) -> list[tuple[int, str]]:
    note_paths_ordered = await asyncio.run(_sort_fp_mtimes(note_paths))
    meta_texts = await asyncio.gather(*[_load_category_meta(i, f) for i, f in enumerate(note_paths_ordered)])
    meta_texts = cast(meta_texts, list[tuple[int, str]])
    return meta_texts


class FileSystemBackend(BackendProtocol):
    _category_files: Optional["CategoryFiles"]
    _category_meta: Optional["CategoryNoteMeta"]
    _notes: Optional[list[MarkdownNoteDict]]

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
        self._category_files = None
        self._category_meta = None
        self._index = None
        self._category_metadata = None

    def _discover_notes(self):
        """
        Read `self.storage_path` looking for children folders and the associated notes within each

        Notes
        -----
        Does not read the notes, only gathers a listing of them
        """
        categories, folders = zip(*[(f.name, f) for f in self.storage_path.iterdir() if f.is_dir()])
        notes = defaultdict(lambda: list())
        for folder in folders:
            notes[folder.name] = [f for f in folder.iterdir() if f.is_file()]
        self._category_files = notes

    def _load_category_meta(self, category: str):
        category_files = self.category_files[category]
        meta_texts: list[tuple[int, str]] = asyncio.run(_load_category_metas(category_files))
        self._category_meta = [MarkdownNoteMeta(idx=i, text=text, file=f).to_dict() for i, text, f in meta_texts]


    @property
    def category_files(self):
        if not self._category_files:
            self._discover_notes()
        return self.category_files

    @property
    def category_meta(self):
        if not self._category_meta:
            self._load_category_meta(self.current_category)
        return self._category_meta

    def _read_category_notes(self, category: str):
        ...



    @property
    def notes(self) -> "CategoryFiles":
        if not self._category_files:
            self._discover_notes()
        return self._category_files

    @property
    def categories(self) -> list[str]:
        return list(self._category_files.keys())

    @property
    def current_category(self) -> Optional[str]:
        return self._current_category

    @current_category.setter
    def current_category(self, value: Optional[str]):
        if not value:
            self._current_category = None
            self._notes = None
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
