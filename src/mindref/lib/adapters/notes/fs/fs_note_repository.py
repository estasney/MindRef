from __future__ import annotations

import shutil
from collections import namedtuple
from collections.abc import Callable, Iterable
from functools import partial
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import TYPE_CHECKING

from kivy import Logger
from lib.adapters.notes.note_repository import (
    AbstractNoteRepository,
)
from lib.domain.events import (
    DiscoverCategoryEvent,
    NotesQueryErrorFailureEvent,
    NotesQueryNotSetFailureEvent,
)
from lib.domain.markdown_note import MarkdownNote
from lib.domain.note_resource import CategoryResourceFiles
from lib.domain.settings import SortOptions
from lib.utils import def_cb, sch_cb, schedulable
from lib.utils.index import RollingIndex
from lib.widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from os import PathLike

    from lib.domain.editable import EditableNote
    from lib.domain.markdown_note import MarkdownNoteDict
    from lib.domain.protocols import GetApp

TGetCategoriesCallback = Callable[[Iterable[str]], None]


class FileSystemNoteRepository(AbstractNoteRepository):
    category_files: dict[str, CategoryResourceFiles]
    category_sorting: SortOptions
    category_sorting_ascending: bool
    note_sorting: SortOptions
    note_sorting_ascending: bool

    _storage_path: Path | None
    _index: RollingIndex | None

    """
    Categories are defined with directories
    Categories Contain
        - .md Note Files
        - .png | .jpg | .jpeg Category Image File, Optional
    """

    def __init__(
        self,
        get_app: GetApp,
        note_sorting: SortOptions = "Creation Date",
        note_sorting_ascending: bool = False,
        category_sorting: SortOptions = "Creation Date",
        category_sorting_ascending: bool = False,
        **kwargs,
    ):
        self._storage_path = None
        self._index = None
        self._current_category = None
        self.get_app = get_app
        self.note_sorting = note_sorting
        self.note_sorting_ascending = note_sorting_ascending
        self.category_sorting = category_sorting
        self.category_sorting_ascending = category_sorting_ascending

        self.category_files = {}

    def get_categories(self, on_complete: TGetCategoriesCallback) -> list[str]:
        """
        Get a list of category names

        Parameters
        ----------
        on_complete : GetCategoriesCallback
        """
        if not self.configured:
            Logger.error(f"{type(self).__name__} : not configured")
            self.get_app().registry.push_event(
                NotesQueryNotSetFailureEvent(on_complete=None)
            )
            on_complete([])
            return []

        category_folders = (f for f in self.storage_path.iterdir() if f.is_dir())

        match self.category_sorting:
            case "Creation Date":
                category_folders = sorted(
                    category_folders,
                    key=lambda x: x.stat().st_ctime,
                    reverse=not self.category_sorting_ascending,
                )
            case "Title":
                category_folders = sorted(
                    category_folders,
                    key=attrgetter("name"),
                    reverse=not self.category_sorting_ascending,
                )

            case "Last Modified Date":
                category_folders = sorted(
                    category_folders,
                    key=lambda x: x.stat().st_mtime,
                    reverse=not self.category_sorting_ascending,
                )
            case _:
                Logger.error(
                    f"{type(self).__name__} : Unhandled category_sorting {self.category_sorting}"
                )
                self.get_app().registry.push_event(
                    NotesQueryErrorFailureEvent(
                        on_complete=None,
                        error="not_found",
                        message=f"{self.category_sorting} is not a valid category_sorting option",
                    )
                )

        categories = [f.name for f in category_folders]
        on_complete(categories)
        Logger.info(
            f"{type(self).__name__}: get_categories - called {on_complete} with {len(categories)} categories"
        )
        return categories

    def _get_category_meta(self, category: str, refresh: bool):
        category_resource = self.category_files[category]
        md_notes = category_resource.get_md_notes(refresh=refresh).get_md_note_metas()

        return md_notes

    def get_category_meta(
        self,
        category: str,
        on_complete: Callable[[list[MarkdownNoteDict]], None] | None,
        refresh: bool = False,
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
            f"{type(self).__name__}: get_category_meta - [category={category}, on_complete={on_complete!r}]"
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
    def storage_path(self, path: PathLike | None):
        if path is None:
            self._storage_path = None
            return
        if self._storage_path == Path(path):
            return
        # If it's different we need to clear our category_files
        self._storage_path = Path(path)
        self.current_category = None
        self.category_files.clear()

    def discover_category(
        self,
        category: str,
        on_complete: Callable[[CategoryResourceFiles], None] | None,
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
            category,
            category_files,
            sort_strategy=self.note_sorting,
            ascending=self.note_sorting_ascending,
        )

        if on_complete:
            on_complete(category_resource)
        return category_resource

    def discover_categories(self, on_complete: Callable[[], None] | None, *args):
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
    ) -> list[Suggestion] | None:
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
                query in field.lower() for field in field_getter(note_inner)
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
    def current_category(self) -> str | None:
        return self._current_category

    @current_category.setter
    def current_category(self, value: str | None):
        if not value:
            self._current_category = None
            self._index = None
            return
        self._current_category = value
        self._index = RollingIndex(size=len(self.category_files[value].notes))

    def create_category(
        self,
        name: str,
        image_path: Path | str,
        on_complete: Callable[[Path, bool], None],
    ):
        """
        Create a new category on the filesystem

        Parameters
        ----------
        name : str
            Category Name
        image_path : Path
            Path to the image file. This will be copied to the new category folder
        on_complete : Path | None
            An optional callback to be called after the category is created.
            If successful, the callback will be called with the path to the category and True
            If unsuccessful, the callback will be called with the path to the category and False


        """
        category_path = self.storage_path / name
        src_image_path = Path(image_path)
        tgt_image_path = (category_path / name).with_suffix(src_image_path.suffix)

        """
        Order of operations:
        1. Try to create the category folder
          a. If it fails, call the on_complete callback with the category path and False
          b. If it succeeds, schedule a function to copy the image file to the category folder.
          This function will need to be aware of the on_complete callback in case it fails.
        2. Try to copy the image file to the category folder
            a. If it fails, call the on_complete callback with the category path and False
            b. If it succeeds, we need to schedule a function to update the category_files dict
            which will in turn call the on_complete callback with the category path and True
        3. Update the category_files dict
            a. If it fails, call the on_complete callback with the category path and False
            b. If it succeeds, call the on_complete callback with the category path and True
        """

        def create_category_folder(
            category_path_: Path,
            on_success: Callable,
            on_fail: Callable[[Path, bool], None],
        ):
            try:
                category_path_.mkdir(exist_ok=False, parents=False)
            except OSError:
                Logger.error(
                    f"{type(self).__name__}: create_category_folder - Failed to create {name}"
                )
                on_fail(category_path, False)
                return
            bound = schedulable(on_success)
            sch_cb(bound)

        def copy_image_file(
            src, tgt, on_success: Callable, on_fail: Callable[[Path, bool], None]
        ):
            try:
                shutil.copy(src, tgt)
            except OSError:
                Logger.info(
                    f"{type(self).__name__}: copy_image_file - Failed to copy image {src} to {tgt}"
                )
                on_fail(category_path, False)
                return
            bound = schedulable(on_success)
            sch_cb(bound)

        def update_category_files_dict(
            category_name: str, category_path_: Path, on_success: Callable
        ):
            category_resource = self.discover_category(
                category=category_name, on_complete=None
            )
            self.category_files[category_name] = category_resource
            self.get_app().registry.push_event(
                DiscoverCategoryEvent(
                    category=category_name,
                )
            )

            bound = schedulable(on_success, category_path, True)
            sch_cb(bound)

            # We work backwards in the callback chain, binding arguments to the callback

        sch_update_category_files_dict = schedulable(
            update_category_files_dict,
            category_name=name,
            category_path_=category_path,
            on_success=on_complete,
        )

        sch_copy_image_file = schedulable(
            copy_image_file,
            src=src_image_path,
            tgt=tgt_image_path,
            on_success=sch_update_category_files_dict,
            on_fail=on_complete,
        )

        sch_create_category_folder = schedulable(
            create_category_folder,
            category_path_=category_path,
            on_success=sch_copy_image_file,
            on_fail=on_complete,
        )
        sch_cb(sch_create_category_folder)

    def index_size(self):
        if not self._index:
            raise Exception("No Index")
        return self._index.size

    def set_index(self, n: int):
        if not self._index:
            raise Exception("No Index")
        self._index.current = n

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
        Logger.info(f"{type(self).__name__}: _resize_index")

    def save_note(
        self,
        note: EditableNote,
        on_complete: Callable[[MarkdownNote], None] | None,
    ):
        note_is_new = note.md_note is None
        Logger.info(f"{type(self).__name__} : save_note {note}")

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
                write_note = schedulable(
                    fp.write_text, data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_new_note,
                    category=note.category,
                    note_path=fp,
                    callback=None,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{type(self).__name__}: save_note - new note")
            case True, _ as cb:
                fp = (self.storage_path / note.category / note.edit_title).with_suffix(
                    ".md"
                )
                write_note = schedulable(
                    fp.write_text, data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_new_note,
                    category=note.category,
                    note_path=fp,
                    callback=cb,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{type(self).__name__}: save_note - new note")
            case False, None:

                fp = note.md_note.filepath
                write_note = schedulable(
                    fp.write_text, data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_edit_note,
                    category=note.category,
                    note_path=fp,
                    callback=None,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{type(self).__name__}: save_note - edit note")
            case False, _ as cb:
                fp = note.md_note.filepath
                write_note = schedulable(
                    fp.write_text, data=note.edit_text, encoding="utf-8"
                )
                after_write = partial(
                    after_write_edit_note,
                    category=note.category,
                    note_path=fp,
                    callback=cb,
                )
                sch_cb(write_note, after_write)
                Logger.info(f"{type(self).__name__}: save_note - edit note")
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
            raise Exception("No Index")
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

    def category_image_uri(self, category: str) -> Path | None:
        return self.category_files[category].get_image_uri()

    def category_name_unique(self, category: str) -> bool:
        """
        Checks if a category name is unique

        Parameters
        ----------
        category : str
            The category name to check
        """
        lcat = category.lower().strip()
        # Perform a case-insensitive check in our category_files dict
        if lcat in (k.lower().strip() for k in self.category_files.keys()):
            return False

        # We want to check the filesystem for any other categories but can only do this if we have a storage path.
        # We can check that we have a storage path by checking our configured attribute.
        if not self.configured:
            return True

        # Check if the directory exists, since we can access app filesystem, this is an inexpensive check
        # We can't just check if the directory exists, since we may have a category named "Foo" and "foo"
        # Create a generator of all directories in the storage path and lowercase them
        matched = next(
            (
                d
                for d in self.storage_path.iterdir()
                if d.is_dir() and d.name.lower() == lcat
            ),
            None,
        )
        if matched:
            return False
        return True
