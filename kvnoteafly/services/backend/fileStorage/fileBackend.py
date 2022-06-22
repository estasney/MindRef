from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable, Optional, TYPE_CHECKING, Union, cast

from kivy.logger import Logger
from toolz import groupby

from services.backend import BackendProtocol, NoteIndex
from services.backend.fileStorage.utils import (
    _load_category_notes,
    discover_folder_notes,
    get_folder_files,
)
from services.utils import LazyLoaded, LazyRegistry
from services.domain import MarkdownNote
from services.editor import EditableNote, TextNote

if TYPE_CHECKING:
    from services.backend.fileStorage.utils import CategoryNoteMeta, CategoryFiles


class FileSystemBackend(BackendProtocol):
    _index: Optional[NoteIndex]
    _current_category: Optional[str]
    _storage_path: Optional[Path]
    category_files: "LazyLoaded[CategoryFiles]" = LazyLoaded()
    category_meta: "LazyLoaded[CategoryNoteMeta]" = LazyLoaded(default=list)
    registry = LazyRegistry()

    """
    Categories are defined with directories
    Individual notes defined as markdown files within their respective categories
    
    Notifies
    --------
    self._discover_notes -> note_files : tuple[category_name, img_path]
        Images in category folders
    
    
    """

    def __init__(self, new_first):
        self._storage_path = None
        self.new_first = new_first
        self._category_files = None
        self._category_meta = []
        self._current_category = None
        self._index = None
        self.registry.note_files(self.save_note_listener)

    @category_files
    def _discover_notes(self):
        """
        Read `self.storage_path` looking for children folders and the associated notes within each.

        Notifies 'note_files' with Note Files
        Notifies 'category_images' with Category Images

        Notes
        -----
        Does not read the notes, only gathers a listing of them
        """
        note_files_bulk = asyncio.run(
            get_folder_files(self.storage_path, discover=discover_folder_notes)
        )

        # Separate notes from images
        def is_md(p: Path):
            return p.suffix == ".md"

        note_files = {}
        img_files = []
        for category_name, cat_files in note_files_bulk.items():
            note_groups = groupby(is_md, cat_files)
            note_files[category_name] = note_groups.get(True, [])
            if img := note_groups.get(False):
                img_files.append((category_name, img[0]))

        self.registry.note_files.notify("discovery", note_files, None)
        self.registry.category_images.notify(img_files)
        return note_files

    @category_meta
    def _load_category_meta(self):
        category_files = self.category_files[self.current_category]
        category_notes = asyncio.run(
            _load_category_notes(
                self.current_category, category_files, new_first=self.new_first
            )
        )
        category_notes = cast(list[MarkdownNote], category_notes)
        category_note_dicts = [note.to_dict() for note in category_notes]
        self.registry.note_meta.notify(category_note_dicts)
        return category_note_dicts

    @property
    def categories(self) -> list[str]:
        try:
            return list(self.category_files.keys())
        except AttributeError:
            return []

    @property
    def current_category(self) -> Optional[str]:
        return self._current_category

    @property
    def storage_path(self) -> Path:
        if not self._storage_path:
            raise AttributeError("Storage Path not set")
        return self._storage_path

    @storage_path.setter
    def storage_path(self, value: Path | str):
        self._storage_path = Path(value)

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
        return MarkdownNote(
            category=category,
            idx=index,
            file=note_file,
        )

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

    def refresh_categories(self):
        # noinspection PyTypeChecker
        self.category_files = None
        getattr(self, "category_files")
        # noinspection PyTypeChecker
        self.category_meta = None

    def refresh_current_category(self):
        """Read contents of current category folder"""
        current = self.current_category
        self.current_category = None
        self.current_category = current

    def save_note_listener(
        self,
        event: str,
        note: "Union[TextNote, EditableNote]",
        callback: Optional[Callable[[MarkdownNote], None]],
        *args,
        **kwargs,
    ):

        if event != "save_note" or not callback:
            Logger.debug(f"fileBackend ignoring event {event}")
            return
        Logger.debug(
            f"fileBackend processing event: {event}, note: {note}, callback: {callback}"
        )
        if isinstance(note, TextNote):
            Logger.debug(f"Processing TextNote")
            note_filepath = (
                Path(self.storage_path) / note.category / note.filename
            ).with_suffix(".md")
            if not note_filepath.parent.exists():
                raise FileNotFoundError(f"Category {note_filepath.parent} not found")
            note_filepath.write_text(note.text)
            self.refresh_categories()
            matched_file_idx, matched_file = next(
                (
                    (i, cf)
                    for i, cf in enumerate(self.category_files[note.category])
                    if cf == note_filepath
                )
            )
            callback(
                MarkdownNote(
                    category=note.category, idx=matched_file_idx, file=matched_file
                )
            )

        elif note is EditableNote:
            Logger.debug(f"Processing EditableNote")
            md_note = note.note
            md_note.file.write_text(note.edit_text, encoding="utf-8")
            Logger.debug(f"Saved File To {md_note.file}")

            callback(
                MarkdownNote(
                    category=md_note.category, idx=md_note.idx, file=md_note.file
                )
            )
