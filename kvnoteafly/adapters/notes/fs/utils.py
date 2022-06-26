from __future__ import annotations

import asyncio
from _operator import itemgetter

from pathlib import Path
from typing import Any, Callable, Coroutine, Mapping

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


async def discover_folder_notes(
    folder: Path, new_first: bool = True
) -> tuple[Path, list[Path]]:
    notes = [f for f in folder.iterdir() if f.is_file()]
    ordered_notes = await _sort_fp_mtimes(notes, new_first)
    return folder, ordered_notes


async def get_folder_files(folder: Path, discover: DiscoverType, **discover_kwargs):
    candidates = [(f.name, f) for f in folder.iterdir() if f.is_dir()]
    if not candidates:
        return {}
    categories, folders = zip(*candidates)
    folder_notes = await asyncio.gather(
        *[discover(f, **discover_kwargs) for f in folders]
    )
    return {folder.name: items for folder, items in folder_notes}
