from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from operator import attrgetter, ge, gt, le, lt
from pathlib import Path

from kivy import Logger
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


@dataclass
class CategoryResourceFiles:
    category: str
    image: ImageResourceFile | None
    sort_strategy: SortOptions
    ascending: bool
    notes: list[NoteResourceFile] = field(default_factory=list)

    @classmethod
    def from_files(
        cls,
        category: str,
        files: Iterable[Path],
        sort_strategy: SortOptions,
        ascending: bool,
    ):
        match sort_strategy:
            case "Creation Date":
                sorted_files = sorted(
                    files, key=lambda x: x.stat().st_mtime_ns, reverse=not ascending
                )
            case "Title":
                sorted_files = sorted(
                    files, key=lambda x: x.name, reverse=not ascending
                )
            case "Last Modified Date":
                sorted_files = sorted(
                    files, key=lambda x: x.stat().st_mtime_ns, reverse=not ascending
                )
            case _:
                Logger.error(f"Invalid sort_strategy: {sort_strategy}")
                sorted_files = sorted(
                    files, key=lambda x: x.stat().st_mtime_ns, reverse=not ascending
                )

        resources = [ResourceFile.to_concrete(f, category) for f in sorted_files]
        resource_groups = groupby(attrgetter("is_image"), resources)
        image = resource_groups.get(True, None)
        notes: list[NoteResourceFile] = resource_groups.get(False, [])
        resource_groups.clear()

        # Assign the index for notes
        for i, note in enumerate(notes):
            note.set_index(i)

        if image:
            n_img = len(image)
            if n_img > 1:
                Logger.warning(
                    f"{cls.__class__.__name__}: from_files - multiple images found - [category='{category}']"
                )
                matched_image = next(
                    (img for img in image if img.path.stem == category.lower()), None
                )
                image = matched_image if matched_image else image[0]
            elif n_img == 1:
                image = image[0]
            else:
                image = None

        return CategoryResourceFiles(
            category=category,
            image=image,
            notes=notes,
            sort_strategy=sort_strategy,
            ascending=ascending,
        )

    def update_note_ages(self, *args):
        """
        Update the age of all notes. This could invalidate the index order
        """

        def get_age(note_inner: "NoteResourceFile"):
            return note_inner.path.stat().st_mtime_ns

        if args:
            for note in args:
                note.age = get_age(note)
        else:
            for note in self.notes:
                note.age = get_age(note)

    def reindex_notes(self):
        """Recalculate indices of `self.notes`

        See Also
        ----------
        `update_note_ages`
        """

        match self.sort_strategy:
            case "Creation Date":

                def sort_func(x):
                    return x.path.stat().st_ctime_ns
            case "Title":

                def sort_func(x):
                    return x.path.name
            case "Last Modified Date":

                def sort_func(x):
                    return x.path.stat().st_mtime_ns
            case _:
                Logger.error(f"Invalid sort_strategy: {self.sort_strategy}")

                def sort_func(x):
                    return x.path.stat().st_mtime_ns

        self.notes.sort(key=sort_func, reverse=not self.ascending)
        for i, note in enumerate(self.notes):
            note.set_index(i)

    def add_note_from_path(self, fp: "Path") -> NoteResourceFile:
        """
        Add a path to `self.notes`, from a Path
        """
        resource = NoteResourceFile(
            path=fp,
            age=fp.stat().st_mtime_ns,
            is_image=False,
            index_=-1,
            category=self.category,
        )
        self.notes.append(resource)
        # This should be the head or tail, so skip updating ages
        self.reindex_notes()
        return resource

    def get_md_notes(self, refresh: bool = False):
        """
        Load a MarkdownFile for each Note

        Parameters
        ----------
        refresh : bool, False
            If False, only notes without Markdown files will be read
            If True, all notes will be read

        Returns
        -------
        """
        if not refresh:
            targets = (note for note in self.notes if note.note_ is None)
            params = {"refresh": False}
        else:
            targets = (note for note in self.notes)
            params = {"refresh": True}

        func = attrgetter("get_note")

        with ThreadPoolExecutor() as executor:
            pipeline = [executor.submit(func(note), **params) for note in targets]
            for future in as_completed(pipeline):
                future.result()

        return self

    def get_md_note_metas(self) -> list[MarkdownNoteDict]:
        return [note.get_note().to_dict() for note in self.notes]

    def get_image_uri(self) -> Path | None:
        if img := self.image:
            return img.path
        return None

    def get_note_by_idx(self, idx) -> NoteResourceFile:
        matched_note = next((note for note in self.notes if note.index_ == idx), None)
        if not matched_note:
            raise IndexError(f"{idx} not found")
        return matched_note

    def get_note_by_path(self, path: Path) -> NoteResourceFile:
        matched_note = next((note for note in self.notes if note.path == path), None)
        if not matched_note:
            raise IndexError(f"{path} not found")
        return matched_note
