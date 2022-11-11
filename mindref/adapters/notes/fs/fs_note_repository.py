from __future__ import annotations

from collections import namedtuple
from functools import cache, partial
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Callable, Iterable, Optional, TYPE_CHECKING

from kivy import Logger
from toolz import groupby

from adapters.notes.fs.utils import (
    _load_category_notes,
    discover_folder_notes,
)
from adapters.notes.note_repository import (
    AbstractNoteRepository,
)
from domain.events import NotesDiscoverCategoryEvent, NotesQueryNotSetFailureEvent
from domain.markdown_note import MarkdownNote
from utils import def_cb, sch_cb
from utils.caching import kivy_cache
from utils.index import RollingIndex
from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from os import PathLike
    from domain.editable import EditableNote
    from domain.markdown_note import MarkdownNoteDict


def category_meta_key_func(*args, **kwargs):
    return kwargs.get("category")


class FileSystemNoteRepository(AbstractNoteRepository):
    _category_files: dict[str, list[Path]]
    _category_imgs: dict[str, Optional[Path]]
    _storage_path: Optional[Path]

    """
    Categories are defined with directories
    Categories Contain
        - .md Note Files
        - .png Category Image File, Optional
    """

    def __init__(self, get_app, new_first: bool):
        super().__init__(get_app, new_first)
        self.new_first = new_first
        self._category_files = {}
        self._category_imgs = {}
        self._storage_path = None
        self._index = None
        self._current_category = None

    def get_categories(self, on_complete: Optional[Callable[[Iterable[str]], None]]):
        """Query for categories"""
        if not self.configured:
            Logger.error(f"{self.__class__.__name__} : not configured")
            self.get_app().registry.push_event(NotesQueryNotSetFailureEvent(None))
            if on_complete:
                return on_complete([])

        category_folders = (f for f in self.storage_path.iterdir() if f.is_dir())
        categories = (f.name for f in category_folders)
        on_complete(categories)

    @kivy_cache(cache_name="category_meta", key_func=category_meta_key_func)
    def _get_category_meta(self, category, *args):

        category_files = self._category_files[category]
        category_notes = _load_category_notes(
            category=self.current_category,
            note_paths=category_files,
            new_first=self.new_first,
        )

        category_note_dicts = [note.to_dict() for note in category_notes]

        return category_note_dicts

    def get_category_meta(
        self,
        category: str,
        on_complete: Optional[Callable[[list["MarkdownNoteDict"]], None]],
    ):
        def scheduled(dt, cat, cb):
            # Simple wrapper to pass result of _get_category_meta to callback
            result = self._get_category_meta(category=cat)
            cb(result)

        if on_complete:
            task = partial(scheduled, cat=category, cb=on_complete)
        else:
            task = partial(self._get_category_meta, category=category)
        sch_cb(task, timeout=0.1)

    @property
    def configured(self) -> bool:
        return self._storage_path is not None

    @property
    def storage_path(self) -> Path:
        if not self._storage_path:
            raise AttributeError("Storage Path not set")
        return self._storage_path

    @storage_path.setter
    def storage_path(self, value: "PathLike"):
        if value is None:
            self._storage_path = None
        else:
            self._storage_path = Path(value)

    def discover_notes(self, on_complete: Optional[Callable[[], None]], *args):
        """
        Find Categories, and associated Note Files
        For Each Category, Found, Pushes a NotesDiscoverCategoryEvent

        """

        def is_md(p: Path):
            return p.suffix == ".md"

        def after_get_categories(categories: Iterable[str]):
            app = self.get_app()
            for category_name in categories:
                category_folder = Path(self.storage_path) / category_name
                category_files = list(
                    discover_folder_notes(category_folder, new_first=self.new_first)
                )

                category_files = groupby(is_md, category_files)
                category_note_files = category_files.get(True, [])
                if category_img := category_files.get(False):
                    category_img = category_img[0]
                Logger.info(category_img)
                self._category_files[category_name] = category_note_files
                self._category_imgs[category_name] = category_img
                app.registry.push_event(
                    NotesDiscoverCategoryEvent(
                        category=category_name,
                        image_path=category_img,
                        notes=category_note_files,
                    )
                )

        if on_complete:
            post_get_cat = def_cb(after_get_categories, on_complete)
        else:
            post_get_cat = after_get_categories

        self.get_categories(post_get_cat)

    def query_notes(
        self, category: str, query: str, on_complete
    ) -> Optional[list[Suggestion]]:
        query = query.lower()
        notes = self._get_category_meta(category=category)
        QueryDoc = namedtuple("QueryDoc", "idx, title, text, score")

        def note_pipeline(note_inner) -> Iterable[QueryDoc]:
            field_getter = itemgetter("idx", "title", "text")
            fields = (field_getter(note) for note in note_inner)
            fields = (QueryDoc(f[0], f[1], f[2], 0) for f in fields)
            yield from fields

        def note_search_pipeline(note_inner: QueryDoc) -> QueryDoc:
            """
            Binary test for string presence
            """
            field_getter = attrgetter("title", "text")
            query_score = sum(
                (query in field.lower() for field in field_getter(note_inner))
            )
            score = query_score
            return QueryDoc(note_inner.idx, *field_getter(note_inner), score)

        def requires_tie_breaker(note_inner: Iterable[QueryDoc]):
            """Test if we have multiples of a score"""
            needs_breaker = False
            seen = set()
            for q_doc in note_inner:
                if q_doc.score in seen:
                    return True
                seen.add(q_doc.score)
            return needs_breaker

        def count_fields(note_inner: QueryDoc) -> int:
            matched_title_count = note_inner.title.lower().count(query)
            matched_text_count = note_inner.text.lower().count(query)
            return note_inner.score + matched_title_count + matched_text_count

        note_haystacks = note_pipeline(notes)
        note_binary = (note_search_pipeline(stack) for stack in note_haystacks)
        note_binary_matches = [note for note in note_binary if note.score > 0]

        if not note_binary_matches:
            return None

        results = []
        if not requires_tie_breaker(note_binary_matches):
            note_binary_matches.sort(key=attrgetter("score"), reverse=True)
        else:
            note_binary_matches.sort(key=count_fields, reverse=True)
        for match in note_binary_matches:
            results.append(Suggestion(title=match.title, index=match.idx))
        return results

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
        self._index = RollingIndex(size=len(self._category_files[value]))

    def index_size(self):
        if not self._index:
            raise Exception("No Index")
        return self._index.size

    def set_index(self, n: int):
        if not self._index:
            raise Exception("No Index")
        self._index.set_current(n)

    @property
    def index(self) -> RollingIndex:
        if not self._index:
            raise AttributeError("No Index")
        return self._index

    def get_note(self, category: str, idx: int, on_complete) -> MarkdownNote:
        note_file = self._category_files[category][idx]
        return MarkdownNote.from_file(
            category=category,
            idx=idx,
            fp=note_file,
        )

    def save_note(self, note: "EditableNote", on_complete) -> MarkdownNote:
        note_is_new = bool(note.edit_title)

        if note_is_new:
            # Construct filepath
            fp = (self.storage_path / note.category / note.edit_title).with_suffix(
                ".md"
            )
            fp.write_text(note.edit_text, encoding="utf-8")

            return MarkdownNote.from_file(note.category, note.idx, fp)

        else:
            md_note = note.md_note
            md_note.text = note.edit_text
            md_note.filepath.write_text(md_note.text, encoding="utf-8")
        return MarkdownNote.from_file(md_note.category, md_note.idx, md_note.filepath)

    def get_next_note(self, on_complete) -> MarkdownNote:
        if not self._index:
            raise Exception(f"No Index")
        self._index.next()
        return self.get_note(
            category=self.current_category, idx=self.index.current, on_complete=None
        )

    def get_previous_note(self, on_complete) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        self._index.previous()
        return self.get_note(
            category=self.current_category, idx=self.index.current, on_complete=None
        )

    def get_current_note(self, on_complete) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        return self.get_note(
            category=self.current_category, idx=self.index.current, on_complete=None
        )

    def category_image_uri(self, category: str) -> Optional[Path]:
        return self._category_imgs.get(category)
