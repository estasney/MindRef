from __future__ import annotations

import asyncio
from _operator import itemgetter

from pathlib import Path
from typing import Any, Callable, Coroutine, Generator, Mapping

from domain.markdown_note import MarkdownNote

CategoryFiles = Mapping[str, list[Path]]
CategoryNoteMeta = list[MarkdownNote]
DiscoverType = Callable[[Any, Any], Coroutine[Any, Any, tuple[Path, list[Path]]]]


async def _fetch_fp_mtime(f: Path) -> tuple[Path, int]:
    return f, f.lstat().st_mtime_ns


async def _sort_fp_mtimes(files: list[Path], new_first: bool) -> list[Path]:
    """Fetch and sort file modified times

    Parameters
    ----------
    new_first
    """
    fetched = await asyncio.gather(*[_fetch_fp_mtime(f) for f in files])
    fetched = sorted(fetched, key=itemgetter(1), reverse=new_first)
    return [f for f, _ in fetched]


async def _load_category_meta(i: int, note_path: Path) -> tuple[int, str, Path]:
    with note_path.open(mode="r", encoding="utf-8") as fp:
        note_text = fp.read()
    return i, note_text, note_path


async def _load_category_metas(note_paths: list[Path], new_first: bool):
    note_paths_ordered = await _sort_fp_mtimes(note_paths, new_first)
    meta_texts = await asyncio.gather(
        *[_load_category_meta(i, f) for i, f in enumerate(note_paths_ordered)]
    )
    return meta_texts


async def _load_category_note(i: int, category: str, note_path: Path) -> MarkdownNote:
    return MarkdownNote.from_file(category=category, idx=i, fp=note_path)


async def _load_category_notes(category: str, note_paths: list[Path], new_first: bool):
    note_paths_ordered = await _sort_fp_mtimes(note_paths, new_first)
    notes = await asyncio.gather(
        *[_load_category_note(i, category, f) for i, f in enumerate(note_paths_ordered)]
    )
    return notes


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
