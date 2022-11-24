from __future__ import annotations

from collections import namedtuple
from functools import partial
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Callable, Iterable, Optional, TYPE_CHECKING

from kivy import Logger

from adapters.notes.note_repository import (
    AbstractNoteRepository,
)
from domain.events import DiscoverCategoryEvent, NotesQueryNotSetFailureEvent
from domain.markdown_note import MarkdownNote
from domain.note_resource import CategoryResourceFiles
from utils import caller, def_cb, sch_cb
from utils.index import RollingIndex
from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from os import PathLike
    from domain.editable import EditableNote
    from domain.markdown_note import MarkdownNoteDict
    from domain.protocols import GetApp

TGetCategoriesCallback = Callable[[Iterable[str]], None]


class FileSystemNoteRepository(AbstractNoteRepository):
    category_files: dict[str, CategoryResourceFiles]
    _storage_path: Optional[Path]
    _index: Optional[RollingIndex]

    """
    Categories are defined with directories
    Categories Contain
        - .md Note Files
        - .png Category Image File, Optional
    """

    def __init__(self, get_app: "GetApp", new_first: bool):
        self._storage_path = None
        self._index = None
        self._current_category = None

        self.get_app = get_app
        self.new_first = new_first
        self.category_files = {}

    def get_categories(self, on_complete: TGetCategoriesCallback) -> list[str]:
        """
        Get a list of category names

        Parameters
        ----------
        on_complete : GetCategoriesCallback
        """
        if not self.configured:
            Logger.error(f"{self.__class__.__name__} : not configured")
            self.get_app().registry.push_event(
                NotesQueryNotSetFailureEvent(on_complete=None)
            )
            on_complete([])
            return []

        category_folders = (f for f in self.storage_path.iterdir() if f.is_dir())
        categories = [f.name for f in category_folders]
        on_complete(categories)
        Logger.info(
            f"{self.__class__.__name__}: get_categories - called {on_complete} with {len(categories)} categories"
        )
        return categories

    def _get_category_meta(self, category, refresh: bool):
        category_resource = self.category_files[category]
        md_notes = category_resource.get_md_notes(refresh=refresh).get_md_note_metas()

        return md_notes

    def get_category_meta(
        self,
        category: str,
        on_complete: Optional[Callable[[list["MarkdownNoteDict"]], None]],
        refresh=False,
    ):
        def scheduled(_, cat, cb):
            # Simple wrapper to pass result of _get_category_meta to callback
            result = self._get_category_meta(category=cat, refresh=refresh)
            cb(result)

        if on_complete:
            task = partial(scheduled, cat=category, cb=on_complete)
        else:
            task = partial(self._get_category_meta, category=category)
        Logger.info(
            f"{self.__class__.__name__}: get_category_meta - [category={category}, on_complete={on_complete!r}]"
        )
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

    def discover_category(
        self,
        category: str,
        on_complete: Optional[Callable[[CategoryResourceFiles], None]],
    ) -> CategoryResourceFiles:
        """
        Find a categories notes and image file

        Parameters
        ----------
        category : str
        on_complete

        Returns
        -------
        """
        category_folder = self.storage_path / category
        category_files = category_folder.iterdir()
        category_resource = CategoryResourceFiles.from_files(
            category, category_files, self.new_first
        )
        if on_complete:
            on_complete(category_resource)
        return category_resource

    def discover_categories(self, on_complete: Optional[Callable[[], None]], *args):
        """
        Find Categories, and associated image files
        For Each Category Found, Pushes a DiscoverCategoryEvent
        """

        def after_get_categories(categories: Iterable[str]):
            app = self.get_app()
            for category_name in categories:
                category_resource = self.discover_category(
                    category=category_name, on_complete=None
                )
                self.category_files[category_name] = category_resource
                app.registry.push_event(
                    DiscoverCategoryEvent(
                        category=category_name,
                    )
                )

        if on_complete:
            post_get_cat = def_cb(after_get_categories, on_complete)
        else:
            post_get_cat = after_get_categories
        self.category_files.clear()
        self.get_categories(on_complete=post_get_cat)

    def query_notes(
        self, category: str, query: str, on_complete
    ) -> Optional[list[Suggestion]]:
        query = query.lower()
        notes = self._get_category_meta(category=category, refresh=False)
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
        self._index = RollingIndex(size=len(self.category_files[value].notes))

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

    def _resize_index(self):
        if not self.current_category:
            raise AttributeError("No Index")
        self._index = RollingIndex(
            size=len(self.category_files[self.current_category].notes)
        )
        Logger.info(f"{self.__class__.__name__}: _resize_index")

    def save_note(
        self,
        note: "EditableNote",
        on_complete: Optional[Callable[["MarkdownNote"], None]],
    ):
        note_is_new = note.md_note is None
        Logger.info(f"{self.__class__.__name__} : save_note {note}")

        def after_write_new_note(_, category, note_path, callback):
            note_resource = self.category_files[category].add_note_from_path(note_path)
            md_note_inner = note_resource.get_note(refresh=True)
            self._resize_index()
            if callback:
                callback(md_note_inner)
            return md_note_inner

        def after_write_edit_note(_, category, note_path, callback):
            category_resource = self.category_files[category]
            note_resource = category_resource.get_note_by_path(note_path)
            category_resource.update_note_ages(note_resource)
            md_note_inner = note_resource.get_note(refresh=True)
            category_resource.reindex_notes()
            if callback:
                callback(md_note_inner)
            return md_note_inner

        match (note_is_new, on_complete):
            case True, None:
                fp = (self.storage_path / note.category / note.edit_title).with_suffix(
                    ".md"
                )
                write_note = caller(
                    fp, "write_text", data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_new_note,
                    category=note.category,
                    note_path=fp,
                    callback=None,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{self.__class__.__name__}: save_note - new note")
            case True, _ as cb:
                fp = (self.storage_path / note.category / note.edit_title).with_suffix(
                    ".md"
                )
                write_note = caller(
                    fp, "write_text", data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_new_note,
                    category=note.category,
                    note_path=fp,
                    callback=cb,
                )

                sch_cb(write_note, after_write)
                Logger.info(f"{self.__class__.__name__}: save_note - new note")
            case False, None:

                fp = note.md_note.filepath
                write_note = caller(
                    fp, "write_text", data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_edit_note,
                    category=note.category,
                    note_path=fp,
                    callback=None,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{self.__class__.__name__}: save_note - edit note")
            case False, _ as cb:
                fp = note.md_note.filepath
                write_note = caller(
                    fp, "write_text", data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_edit_note,
                    category=note.category,
                    note_path=fp,
                    callback=cb,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{self.__class__.__name__}: save_note - edit note")
            case _:
                raise Exception("Logic Error")

    def get_note(self, category: str, idx: int, on_complete) -> MarkdownNote:
        # TODO IndexError - Show a new note page
        resource = self.category_files[category].get_note_by_idx(idx)
        md_note = resource.get_note()
        if on_complete:
            on_complete(md_note)
        return md_note

    def get_next_note(self, on_complete) -> MarkdownNote:
        if not self._index:
            raise Exception(f"No Index")
        self._index.next()
        return self.get_note(
            category=self.current_category,
            idx=self.index.current,
            on_complete=on_complete,
        )

    def get_previous_note(self, on_complete) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        self._index.previous()
        return self.get_note(
            category=self.current_category,
            idx=self.index.current,
            on_complete=on_complete,
        )

    def get_current_note(self, on_complete) -> MarkdownNote:
        if not self._index:
            raise Exception("No Index")
        return self.get_note(
            category=self.current_category,
            idx=self.index.current,
            on_complete=on_complete,
        )

    def category_image_uri(self, category: str) -> Optional[Path]:
        return self.category_files[category].get_image_uri()
