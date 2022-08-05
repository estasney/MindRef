from __future__ import annotations

import io
from _operator import itemgetter
from dataclasses import asdict, dataclass
from os import PathLike
from pathlib import Path
from typing import Generator, Optional, Protocol, TYPE_CHECKING, TypedDict

from domain.parser.markdown_parser import MarkdownParser

if TYPE_CHECKING:
    from domain.md_parser_types import MD_DOCUMENT, MdHeading, MdBlockCode


class FileLikeProtocol(Protocol):
    def read(self):
        ...

    def write(self):
        ...


class MarkdownNoteDict(TypedDict):
    category: str
    text: str
    title: str
    idx: int
    filepath: Optional[Path]
    document: "MD_DOCUMENT"


@dataclass
class MarkdownNote:
    parser = MarkdownParser()

    category: str
    text: str
    title: str
    idx: int
    filepath: Optional[Path]
    document: "MD_DOCUMENT"

    def to_dict(self) -> MarkdownNoteDict:
        return asdict(self, dict_factory=MarkdownNoteDict)

    @classmethod
    def from_file(cls, category: str, idx: int, fp: PathLike):
        filepath = Path(fp)
        text = filepath.read_text(encoding="utf-8")
        document = cls.parser.parse(text)
        document, doc_title = cls._get_title_from_doc(document)
        if not doc_title:
            doc_title = filepath.stem.title()
        return MarkdownNote(
            category=category,
            text=text,
            title=doc_title,
            idx=idx,
            filepath=filepath,
            document=document,
        )

    @classmethod
    def from_buffer(
        cls,
        category: str,
        idx: int,
        buffer: io.StringIO,
        title: str,
        filepath: Optional[Path],
    ):
        text = buffer.read()
        document = cls.parser.parse(text)
        document, doc_title = cls._get_title_from_doc(document)
        return MarkdownNote(
            category=category,
            text=text,
            title=title,
            idx=idx,
            filepath=filepath,
            document=document,
        )

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
