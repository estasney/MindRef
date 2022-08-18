from __future__ import annotations

from _operator import attrgetter, itemgetter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Generator, Iterable, Mapping, Sequence

from domain.markdown_note import MarkdownNote

CategoryFiles = Mapping[str, list[Path]]
CategoryNoteMeta = list[MarkdownNote]


def _load_category_note(i: int, category: str, note_path: Path) -> MarkdownNote:
    return MarkdownNote.from_file(category=category, idx=i, fp=note_path)


def _load_category_notes(
    category: str, note_paths: Sequence[Path], new_first: bool
) -> Iterable[MarkdownNote]:
    """
    Given a category, load MarkdownNote for each of its files

    Parameters
    ----------
    category : str
        Name of category
    note_paths : Sequence[Path]
        File paths
    new_first : bool
        Determines ordering by `st_mtime_ns`

    Returns
    -------
    """
    notes = ((f, f.lstat().st_mtime_ns) for f in note_paths)
    notes = sorted(notes, key=itemgetter(1), reverse=new_first)
    notes = (f for f, _ in notes)

    with ThreadPoolExecutor() as executor:
        pipeline = [
            executor.submit(
                _load_category_note, i=i, category=category, note_path=note_path
            )
            for i, note_path in enumerate(notes)
        ]
        output = []
        for future in as_completed(pipeline):
            output.append(future.result())

    return sorted(output, key=attrgetter("idx"), reverse=not new_first)


def discover_folder_notes(
    folder: Path, new_first: bool = True
) -> Generator[Path, None, None]:
    """
    Get files in folder, sorted by `st_mtime_ns`
    Parameters
    ----------
    folder : Path
        Folder to Search
    new_first : bool, defaults to True
        If True, newer files appear first
    """
    notes = ((f, f.lstat().st_mtime_ns) for f in folder.iterdir() if f.is_file())
    sorted_notes = sorted(notes, key=itemgetter(1), reverse=new_first)
    for note, _ in sorted_notes:
        yield note
