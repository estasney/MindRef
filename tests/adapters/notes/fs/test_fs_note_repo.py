from functools import reduce
from itertools import combinations, product
from operator import and_, attrgetter
from typing import Callable, Optional

import pytest
from toolz import sliding_window

from adapters.notes.fs.fs_note_repository import FileSystemNoteRepository
from pathlib import Path

from domain.markdown_note import MarkdownNote


@pytest.mark.parametrize("n_categories", [0, 1, 2, 3])
def test_category_discovery(n_categories, category_folders):
    expected_folders, root_folder = category_folders(n_categories)
    fs = FileSystemNoteRepository(new_first=True, get_app=lambda: None)
    fs.storage_path = root_folder
    discovery = list(fs.discover_notes())
    for folder, img in expected_folders:
        assert folder.name in fs.categories
        assert folder.name in ((d.category for d in discovery))
        assert img in ((d.image_path for d in discovery))


@pytest.fixture()
def notes():
    note_files = (Path(__file__).parent / "data").glob("*.md")
    return [
        MarkdownNote.from_file(category="test", idx=i, fp=fp)
        for i, fp in enumerate(note_files)
    ]


@pytest.fixture()
def title_query_generator():
    def title_query_generator_(
        matched: list[MarkdownNote], unmatched: Optional[list[MarkdownNote]]
    ):
        get_title: Callable[[MarkdownNote], str] = attrgetter("title")
        matched_titles = [get_title(n).lower() for n in matched]
        unmatched_titles = (
            [get_title(n).lower() for n in unmatched] if unmatched else None
        )

        def query_gen(grp: list[str]):
            # Generate queries that will match the grp
            common_chars = reduce(and_, (set(t) for t in grp))
            if len(common_chars) < 3:
                raise AssertionError(
                    f"{', '.join(grp)} only share {len(common_chars)}, {','.join(sorted(common_chars))}"
                )

            # Use sliding windows and generators to generate queries that match the grp
            chunks = product(*(sliding_window(3, t) for t in grp))
            for chunk in chunks:
                sc = set(("".join(chars) for chars in chunk))
                if len(sc) == 1:
                    yield "".join(chunk[0])

        def query_pipeline():
            matched_title_gen = query_gen(matched_titles)
            if not unmatched_titles:
                return next(matched_title_gen)
            for query in matched_title_gen:
                if not any((query in ut for ut in unmatched_titles)):
                    return query

        return query_pipeline()

    return title_query_generator_


@pytest.mark.parametrize("matching", [(slice(2), None)])
def test_query_notes(matching, notes, title_query_generator, monkeypatch):
    """
    - Given a collection of notes, and a query
    - Query the notes for matches in the text and title
    - Check for false positives, false negatives and ranking
    """
    match_idx, no_match_idx = matching
    match_notes = notes[match_idx]
    unmatched_notes = notes[no_match_idx] if no_match_idx else None
    q = title_query_generator(match_notes, unmatched_notes)
    fs = FileSystemNoteRepository(new_first=True, get_app=lambda: None)

    def patch_meta(*args, **kwargs):
        return [note.to_dict() for note in notes]

    monkeypatch.setattr(fs, "_load_category_meta", patch_meta)
    result = fs.query_notes("test", q)
    for suggestion in result:
        assert suggestion.title in (n.title for n in match_notes)
        if unmatched_notes:
            assert suggestion.title not in (n.title for n in unmatched_notes)
