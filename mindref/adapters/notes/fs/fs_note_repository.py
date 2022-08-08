from __future__ import annotations

from pathlib import Path
from typing import Generator, NamedTuple, Optional, TYPE_CHECKING

from toolz import groupby

from adapters.notes.fs.utils import (
    _load_category_notes,
    discover_folder_notes,
)
from adapters.notes.note_repository import (
    AbstractNoteRepository,
    NoteIndex,
)
from domain.markdown_note import MarkdownNote

if TYPE_CHECKING:
    from os import PathLike
    from domain.editable import EditableNote
    from domain.markdown_note import MarkdownNoteDict


class NoteDiscovery(NamedTuple):
    category: str
    image_path: Optional[Path]
    notes: list[Path]


class FileSystemNoteRepository(AbstractNoteRepository):
    _category_files: dict[str, list[Path]]

    """
    Categories are defined with directories
    Individual notes defined as markdown files within their respective categories
    
    Notifies
    --------
    self._discover_notes -> note_files : tuple[category_name, img_path]
        Images in category folders
    """

    def __init__(self, get_app, new_first: bool):
        super().__init__(get_app)
        self.new_first = new_first
        self._category_files = {}
        self._storage_path = None
        self._index = None

    @property
    def storage_path(self) -> Path:
        if not self._storage_path:
            raise AttributeError("Storage Path not set")
        return self._storage_path

    @storage_path.setter
    def storage_path(self, value: "PathLike"):
        self._storage_path = Path(value)

    def discover_notes(self, *args) -> Generator[NoteDiscovery, None, None]:
        """
        Read `self.storage_path` looking for category folders, their notes, and optional image

        Notes
        -----
        Does not read the notes, only gathers a listing of them

        Yields
        -------
        NoteDiscovery
        """

        category_folders = (f for f in self.storage_path.iterdir() if f.is_dir())

        def is_md(p: Path):
            return p.suffix == ".md"

        for category_folder in category_folders:
            category_name = category_folder.name
            category_files = list(
                discover_folder_notes(category_folder, new_first=self.new_first)
            )
            category_files = groupby(is_md, category_files)
            category_note_files = category_files.get(True, [])
            if category_img := category_files.get(False):
                category_img = category_img[0]
            self._category_files[category_name] = category_note_files
            yield NoteDiscovery(
                category=category_name,
                image_path=category_img,
                notes=category_note_files,
            )

    @property
    def category_meta(self):
        return self._load_category_meta()

    def _load_category_meta(self) -> list["MarkdownNoteDict"]:
        category_files = self._category_files[self.current_category]
        category_notes = _load_category_notes(
            category=self.current_category,
            note_paths=category_files,
            new_first=self.new_first,
        )

        category_note_dicts = [note.to_dict() for note in category_notes]

        return category_note_dicts

    @property
    def categories(self) -> list[str]:
        if not self._category_files:
            # To populate _category_files we have to consume the iterable
            for _ in self.discover_notes():
                ...
        return list(self._category_files.keys())

    @property
    def current_category(self) -> Optional[str]:
        return self._current_category

    @current_category.setter
    def current_category(self, value: Optional[str]):
        if not value:
            self._current_category = None
            self._index = None
            return
        self._current_category = value
        self._index = NoteIndex(size=len(self._category_files[value]))

    def index_size(self):
        if not self._index:
            raise Exception("No Index")
        return self._index.size

    def set_index(self, n: int):
        if not self._index:
            raise Exception("No Index")
        self._index.set_current(n)

    @property
    def index(self) -> NoteIndex:
        if not self._index:
            raise AttributeError("No Index")
        return self._index

    def get_note(self, category: str, idx: int) -> MarkdownNote:
        note_file = self._category_files[category][idx]
        return MarkdownNote.from_file(
            category=category,
            idx=idx,
            fp=note_file,
        )

    def save_note(self, note: "EditableNote") -> MarkdownNote:
        note_is_new = bool(note.edit_title)

        if note_is_new:
            # Construct filepath
            fp = (self.storage_path / note.category / note.edit_title).with_suffix(
                ".md"
            )
            fp.write_text(note.edit_text, encoding="utf-8")
            self.discover_notes()
            return MarkdownNote.from_file(note.category, note.idx, fp)

        else:
            md_note = note.md_note
            md_note.text = note.edit_text
            md_note.filepath.write_text(md_note.text, encoding="utf-8")
        return MarkdownNote.from_file(md_note.category, md_note.idx, md_note.filepath)

    def next_note(self) -> MarkdownNote:
        if not self._index:
            raise Exception(f"No Index")
        self._index.next()
        return self.get_note(category=self.current_category, idx=self.index.current)

    def previous_note(self) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        self._index.previous()
        return self.get_note(category=self.current_category, idx=self.index.current)

    def current_note(self) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        return self.get_note(category=self.current_category, idx=self.index.current)