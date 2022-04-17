from dataclasses import dataclass, field, fields
from typing import Literal, Optional, Union
from marko.block import BlockElement, FencedCode, Heading
from kvnoteafly.custom.markdown.markdown_document import MarkdownDocument


@dataclass
class BaseNote:
    note_type: Literal["shortcut", "code", "markdown"]
    idx: int
    title: str
    category: str


@dataclass
class ShortcutNote(BaseNote):
    keys_str: str
    note_type: Literal["shortcut"] = field(default="shortcut", init=False)


@dataclass
class CodeNote(BaseNote):
    text: str
    lexer: str
    note_type: Literal["code"] = field(default="code", init=False)


@dataclass
class MarkdownNote(BaseNote):
    text: str
    note_type: Literal["markdown"] = field(default="markdown", init=False)


def _get_node_text(blocks: list[BlockElement]) -> str:
    return "\n".join(MarkdownDocument.get_node_text(block).strip() for block in blocks)


def get_note_type(
    idx: int, category: str, blocks: list[BlockElement]
) -> Union[ShortcutNote, CodeNote, MarkdownNote]:
    header_block = next((b for b in blocks if isinstance(b, Heading)), None)
    if not header_block:
        raise Exception("No Title Found")
    title = MarkdownDocument.get_node_text(header_block)
    fenced_block = next((b for b in blocks if isinstance(b, FencedCode)), None)
    if not fenced_block:
        return MarkdownNote(
            idx=idx, title=title, category=category, text=_get_node_text(blocks)
        )
    elif fenced_block.lang == "shortcut":
        return ShortcutNote(
            idx=idx,
            title=title,
            category=category,
            keys_str=_get_node_text([fenced_block]).strip(),
        )
    else:
        return CodeNote(
            idx=idx,
            title=title,
            category=category,
            text=_get_node_text([fenced_block]),
            lexer=fenced_block.lang,
        )
