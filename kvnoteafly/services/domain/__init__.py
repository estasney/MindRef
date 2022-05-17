from __future__ import annotations

from dataclasses import asdict, dataclass, field
from operator import itemgetter
from pathlib import Path
from typing import Generator, TYPE_CHECKING, TypedDict

from services.domain.parser import MarkdownParser

if TYPE_CHECKING:
    from md_parser_types import *


class MarkdownNoteDict(TypedDict):
    text: str
    category: str
    idx: int
    document: "MD_DOCUMENT"
    file: Path
    title: str
    has_shortcut: bool
    shortcut_keys: Optional[tuple[str, ...]]


@dataclass
class MarkdownNote:
    parser = MarkdownParser()

    category: str
    idx: int
    file: Path
    text: str = field(init=False)
    document: "MD_DOCUMENT" = field(init=False)
    title: str = field(init=False)
    has_shortcut: bool = field(init=False, default=False)
    shortcut_keys: Optional[tuple[str, ...]] = field(init=False, default=None)

    def to_dict(self) -> MarkdownNoteDict:
        return asdict(self, dict_factory=MarkdownNoteDict)

    @classmethod
    def _get_title_from_doc(
        cls, document: "MD_DOCUMENT"
    ) -> tuple["MD_DOCUMENT", Optional[str]]:
        def get_header_blocks() -> Generator["MdHeading", None, None]:
            return (node for node in document if node["type"] == "heading")

        headers = get_header_blocks()
        try:
            title_header = min(headers, key=itemgetter("level"))
            title_header_text = title_header["children"][0]["text"]
            if not title_header_text:
                return document, None
            return [
                node for node in document if node != title_header
            ], title_header_text
        except ValueError:
            # no matching headers
            return document, None

    @classmethod
    def _get_block_code(
        cls, document: "MD_DOCUMENT"
    ) -> Generator["MdBlockCode", None, None]:
        return (node for node in document if node["type"] == "block_code")

    @classmethod
    def _get_block_code_shortcut(cls, document: "MD_DOCUMENT") -> Optional[tuple[str]]:
        blocks = cls._get_block_code(document)
        shortcut_block = next(
            (node for node in blocks if node["info"] == "shortcut"), None
        )
        if not shortcut_block:
            return None
        key_chars = tuple((t.strip() for t in shortcut_block["text"].split(",")))
        return key_chars

    def __post_init__(self):
        self.text = self.file.read_text(encoding="utf-8")
        document = self.parser.parse(self.text)
        document, title = self._get_title_from_doc(document)
        if title:
            self.title = title
        self.document = document
        self.shortcut_keys = self._get_block_code_shortcut(document)

        if self.shortcut_keys:
            self.has_shortcut = True
            # Strip out shortcut from text
            head, _, rest = self.text.split("```")
            text = "\n".join((head.strip(), rest.strip())).replace("#", "").strip()
            self.text = text

        if not hasattr(self, "title"):
            # Fallback in case we couldn't parse it in markdown
            self.title = self.file.stem.title()
