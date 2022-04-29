from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, TypedDict
import re
from marko.block import Document, FencedCode, Heading


class MarkdownNoteDict(TypedDict):
    text: str
    category: str
    idx: int
    document: Document
    file: Path
    title: str
    has_shortcut: bool
    shortcut_keys: Optional[tuple[str, ...]]


class NoteMetaDataDict(TypedDict):
    title: str
    idx: int
    has_shortcut: bool
    shortcut_keys: Optional[tuple[str, ...]]


@dataclass
class MarkdownNoteMeta:
    idx: int
    text: str
    file: Path
    title: str = field(init=False)
    has_shortcut: bool = field(init=False, default=False)
    shortcut_keys: Optional[tuple[str, ...]] = field(init=False, default=None)

    SHORTCUT_PATTERN = re.compile(r"(?:`{3}shortcut\s+)([^`\n]+)")
    TITLE_PATTERN = re.compile(r"(?:#+ +)([\w ]+)", flags=re.MULTILINE)

    def to_dict(self) -> NoteMetaDataDict:
        return asdict(self, dict_factory=NoteMetaDataDict)

    def __post_init__(self):
        if title_match := self.TITLE_PATTERN.search(self.text):
            self.title = title_match.group(1)
        if shortcut_match := self.SHORTCUT_PATTERN.search(self.text):
            self.shortcut_keys = tuple((t.strip() for t in shortcut_match.group(1).split(",")))
            self.has_shortcut = True
        if not hasattr(self, 'title'):
            self.title = self.file.stem.title()


@dataclass
class MarkdownNote:
    text: str
    category: str
    idx: int
    document: Document
    file: Path
    title: str = field(init=False)
    has_shortcut: bool = field(init=False, default=False)
    shortcut_keys: Optional[tuple[str, ...]] = field(init=False, default=None)

    def to_dict(self) -> MarkdownNoteDict:
        return asdict(self, dict_factory=MarkdownNoteDict)

    def __post_init__(self):
        for block in self.document.children:
            if isinstance(block, Heading):
                if block.children and block.children[0].children:
                    self.title = block.children[0].children
            if isinstance(block, FencedCode) and block.lang == 'shortcut':
                self.has_shortcut = True
                code_txt = block.children[0].children.strip()
                key_chars = [t.strip() for t in code_txt.split(",")]
                self.shortcut_keys = tuple(key_chars)
        if not hasattr(self, 'title'):
            self.title = self.file.stem.title()
