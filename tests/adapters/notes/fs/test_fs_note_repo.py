import random
import string
from functools import partial, reduce
from itertools import product
from operator import and_, attrgetter
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from lib.domain.note_resource import CategoryResourceFiles
    from lib.widgets.typeahead.typeahead_dropdown import Suggestion

import pytest
from toolz import sliding_window

from lib.adapters.notes.fs.fs_note_repository import FileSystemNoteRepository
from pathlib import Path

from lib.domain.markdown_note import MarkdownNote


@pytest.fixture
def app_registry():
    registry = type("registry", (object,), {"push_event": lambda x: x})
    return type("FakeApp", (object,), {"registry": registry})


@pytest.fixture
def note_repo_factory(
    filesystem_data, app_registry
) -> Callable[..., "FileSystemNoteRepository"]:
    def note_repo_(n_notes: int, category_selected: bool) -> "FileSystemNoteRepository":
        category_files, root_folder = filesystem_data(1, n_notes)
        fs = FileSystemNoteRepository(new_first=True, get_app=lambda: app_registry)
        fs.storage_path = root_folder
        fs.discover_categories(lambda x: x)
        if category_selected:
            cat = next((k for k in category_files.keys()), None)
            fs.current_category = cat.name

        return fs

    r = note_repo_

    return note_repo_


@pytest.mark.parametrize("n_categories", [0, 1, 2, 3])
def test_category_discovery(n_categories, category_folders, app_registry):
    """
    Given directory with 'category' folders
    Call FileSystemNoteRepository.get_categories
    Check that categories and their images are discovered
    """
    expected_folders, root_folder = category_folders(n_categories)
    fs = FileSystemNoteRepository(new_first=True, get_app=lambda: app_registry)
    fs.storage_path = root_folder

    def fs_get_categories_callback(cat):
        assert set(cat) == set(folder.name for folder, _ in expected_folders)

    fs.get_categories(fs_get_categories_callback)

    # Test for category discovery
    def fs_discovery_callback(resource: "CategoryResourceFiles", category_name, img):
        assert resource.category == category_name
        assert resource.image.path == img

    for name, img in ((folder.name, img) for folder, img in expected_folders):
        cb = partial(fs_discovery_callback, category_name=name, img=img)
        fs.discover_category(name, cb)


@pytest.fixture()
def notes():
    note_files = (Path(__file__).parent / "data").glob("*.md")
    return [
        MarkdownNote.from_file(category="test", idx=i, fp=fp)
        for i, fp in enumerate(note_files)
    ]


@pytest.fixture()
def title_query_generator():
    """
    Generate a query that meets the condition of matching matched notes and not matching unmatched notes

    Returns
    -------

    """

    def title_query_generator_(
        matched: list[MarkdownNote], unmatched: Optional[list[MarkdownNote]]
    ):
        get_title: Callable[[MarkdownNote], str] = attrgetter("title")
        matched_titles = [get_title(n).lower() for n in matched] if matched else None
        unmatched_titles = (
            [get_title(n).lower() for n in unmatched] if unmatched else None
        )

        def query_gen(grp: list[str]):
            # Generate queries that will match the grp
            common_chars = reduce(
                and_,
                (
                    set((char for char in t if char not in string.whitespace))
                    for t in grp
                ),
            )
            if len(common_chars) < 3:
                raise AssertionError(
                    f"{', '.join(grp)} only share {len(common_chars)}, {','.join(sorted(common_chars))}"
                )

            # Use sliding windows and generators to generate queries that match the grp
            chunks = product(
                *(
                    sliding_window(
                        3, (char for char in t if char not in string.whitespace)
                    )
                    for t in grp
                )
            )
            for chunk in chunks:
                sc = set(("".join(chars) for chars in chunk))
                if len(sc) == 1:
                    yield "".join(chunk[0])

        def query_pipeline():
            match (matched_titles, unmatched_titles):
                case list(), None:
                    matched_title_gen = query_gen(matched_titles)
                    return next(matched_title_gen)
                case list(), list():
                    matched_title_gen = query_gen(matched_titles)
                    for query in matched_title_gen:
                        if not any((query in ut for ut in unmatched_titles)):
                            return query
                case None, list() | None:
                    # Generate random sequences
                    make_chars = (
                        "".join(random.choices(string.ascii_lowercase, k=3))
                        for _ in range(10_000)
                    )
                    for query in make_chars:
                        if unmatched_titles:
                            if not any((query in ut for ut in unmatched_titles)):
                                return query
                        else:
                            return query

        return query_pipeline()

    return title_query_generator_


def matches_title_or_text(query, suggestion: "Suggestion", notes):
    matches_titles = suggestion.title in (n.title for n in notes)
    matches_text = any(n.text.find(query) for n in notes)
    return matches_text or matches_titles


@pytest.mark.parametrize(
    "matching",
    [(slice(1), None), (slice(2), None), (slice(2), slice(2, 3)), (None, None)],
    ids=lambda x: f"Matched: {x[0]}, Unmatched: {x[1]}",
)
def test_query_notes(matching, notes, title_query_generator, monkeypatch):
    """
    - Given a collection of notes, and a query
    - Query the notes for matches in the text and title
    - Check for false positives, false negatives and ranking
    """
    match_idx, no_match_idx = matching
    match_notes = notes[match_idx] if match_idx else None
    unmatched_notes = notes[no_match_idx] if no_match_idx else None
    q = title_query_generator(match_notes, unmatched_notes)
    fs = FileSystemNoteRepository(new_first=True, get_app=lambda: None)

    def patch_meta(*args, **kwargs):
        return [note.to_dict() for note in notes]

    monkeypatch.setattr(fs, "_get_category_meta", patch_meta)

    result = fs.query_notes(category="test", query=q, on_complete=None)
    if not match_notes and not unmatched_notes:
        assert result is None
        return
    for suggestion in result:
        assert matches_title_or_text(q, suggestion, match_notes)
        if unmatched_notes:
            assert suggestion.title not in (note.title for note in unmatched_notes)


@pytest.mark.parametrize("n_notes", [0, 10])
@pytest.mark.parametrize("cat_selected", [True, False])
def test_index_sizing(n_notes, cat_selected, note_repo_factory):
    """
    Given NoteRepository
    With different categories, including None,
    Check that index size is correct
    Returns
    -------

    """
    fs = note_repo_factory(n_notes=n_notes, category_selected=cat_selected)
    if not cat_selected:
        assert fs.current_category is None
        with pytest.raises(Exception, match="No Index"):
            fs.index_size()
        with pytest.raises(Exception, match="No Index"):
            _ = fs.index
        with pytest.raises(Exception, match="No Index"):
            fs.set_index(0)
        return
    assert fs.index_size() == n_notes
    # Ensure index is cleared when category switches to None
    fs_category = fs.current_category
    fs.current_category = None
    with pytest.raises(Exception, match="No Index"):
        fs.index_size()
    with pytest.raises(Exception, match="No Index"):
        _ = fs.index
    with pytest.raises(Exception, match="No Index"):
        fs.set_index(0)
    fs.current_category = fs_category
    assert fs.index


@pytest.mark.parametrize("n_notes", [0, 10])
@pytest.mark.parametrize("cat_selected", [True, False])
def test_get_note(n_notes, cat_selected, note_repo_factory):
    """
    Given NoteRepository
    Ask To Get a Note By Index
    Check that a valid idx receives a 'MarkdownNote' and Invalid raises
    """

    fs = note_repo_factory(n_notes=n_notes, category_selected=cat_selected)
    if n_notes == 0:
        with pytest.raises(Exception):
            fs.get_note("0", 0, None)
    else:
        assert type(fs.get_note("0", 0, None)) == MarkdownNote


@pytest.mark.parametrize("platform", ["android", "other"])
def test_note_repo_factory(platform, monkeypatch):
    """
    Given a platform
    Use NoteRepositoryFactory to get the correct Repo for platform
    Check that the correct repo is returned

    Returns
    -------
    """
    import kivy

    monkeypatch.setattr(kivy, "platform", platform)

    from lib.adapters.notes.android.android_note_repository import AndroidNoteRepository
    from lib.adapters.notes.note_repository import (
        AbstractNoteRepository,
        NoteRepositoryFactory,
    )

    repo = NoteRepositoryFactory().get_repo()
    assert issubclass(repo, AbstractNoteRepository)
    match platform:
        case "android":
            assert issubclass(repo, (AbstractNoteRepository, AndroidNoteRepository))
        case _:
            assert issubclass(repo, (AbstractNoteRepository, FileSystemNoteRepository))
