from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from operator import attrgetter, ge, gt, le, lt
from pathlib import Path

from kivy.logger import Logger
from toolz import groupby

from mindref.lib.domain.markdown_note import MarkdownNote, MarkdownNoteDict
from mindref.lib.domain.settings import SortOptions


@dataclass(slots=True)
class ResourceFile:
    path: Path
    category: str
    age: int
    is_image: bool
    index_: int = field(default=-1)

    @classmethod
    def to_concrete(
        cls, fp: Path, category: str
    ) -> "NoteResourceFile | ImageResourceFile":
        age = fp.stat().st_mtime_ns
        fp_suffix = fp.suffix.lower() if fp.suffix else None
        match fp_suffix:
            case ".png" | ".jpg" | ".jpeg":
                return ImageResourceFile(
                    path=fp, age=age, is_image=True, category=category
                )
            case _:
                return NoteResourceFile(
                    path=fp, age=age, is_image=False, category=category
                )

    def set_index(self, val: int):
        self.index_ = val
        return self

    def __lt__(self, other: "ResourceFile"):
        return lt(self.age, other.age)

    def __le__(self, other: "ResourceFile"):
        return le(self.age, other.age)

    def __gt__(self, other: "ResourceFile"):
        return gt(self.age, other.age)

    def __ge__(self, other: "ResourceFile"):
        return ge(self.age, other.age)


@dataclass(slots=True)
class NoteResourceFile(ResourceFile):
    is_image = False
    note_: MarkdownNote | None = None

    def get_note(self, refresh=False) -> MarkdownNote:
        match (self.note_, refresh):
            case (None, False | True):
                self.note_ = MarkdownNote.from_file(
                    self.category, self.index_, self.path
                )
                return self.note_
            case (MarkdownNote(), False):
                return self.note_
            case (MarkdownNote(), True):
                self.note_ = MarkdownNote.from_file(
                    self.category, self.index_, self.path
                )
                return self.note_
            case _:
                raise Exception("Logic Error")

    def set_index(self, val: int):
        self.index_ = val
        if self.note_:
            self.note_.idx = self.index_
        return self


@dataclass(slots=True)
class ImageResourceFile(ResourceFile):
    is_image = True
