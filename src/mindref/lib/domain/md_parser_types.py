from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class MdLink(TypedDict):
    type: Literal["link"]
    link: str
    children: list[TMdLinkChildTypes]
    title: str | None


class MdImage(TypedDict):
    type: Literal["image"]
    src: str
    alt: str
    title: str | None


class MdListItem(TypedDict):
    type: Literal["list_item"]
    children: list[TMdBlockChildTypes]
    level: int


class MdListUnordered(TypedDict):
    type: Literal["list"]
    children: list[MdListItem]
    ordered: Literal[False]
    level: int


class MdListOrdered(TypedDict):
    type: Literal["list"]
    children: list[MdListItem]
    ordered: Literal[True]
    level: int
    start: NotRequired[int]


class MdBlockCode(TypedDict):
    type: Literal["block_code"]
    text: str
    info: str | None


class MdThematicBreak(TypedDict):
    type: Literal["thematic_break"]


class MdNewLine(TypedDict):
    type: Literal["newline"]


class MdLineBreak(TypedDict):
    type: Literal["linebreak"]


class MdCodeSpan(TypedDict):
    type: Literal["codespan"]
    text: str


class MdBlockQuote(TypedDict):
    type: Literal["block_quote"]
    children: list[TMdBlockChildTypes]


class MdBlockText(TypedDict):
    type: Literal["block_text"]
    children: list[TMdInlineTypes]


class MdBlockHTML(TypedDict):
    type: Literal["block_html"]
    text: str


class MdText(TypedDict):
    type: Literal["text"]
    text: str


class MdTextEmphasis(TypedDict):
    type: Literal["emphasis"]
    children: list[TMdInlineTypes]


class MdTextStrong(TypedDict):
    type: Literal["strong"]
    children: list[TMdInlineTypes]


class MdHeading(TypedDict):
    type: Literal["heading"]
    children: list[TMdInlineTypes]
    level: int


class MdParagraph(TypedDict):
    type: Literal["paragraph"]
    children: list[TMdInlineTypes]


class MdTableBodyCell(TypedDict):
    type: Literal["table_cell"]
    children: list[TMdInlineTypes]
    align: Literal["left", "right", "center"] | None
    is_head: Literal[False]


class MdTableHeadCell(TypedDict):
    type: Literal["table_cell"]
    children: list[TMdInlineTypes]
    align: Literal["left", "right", "center"] | None
    is_head: Literal[True]


class MdTableBodyRow(TypedDict):
    type: Literal["table_row"]
    children: list[MdTableBodyCell]


class MdTableHead(TypedDict):
    type: Literal["table_head"]
    children: list[MdTableHeadCell]


class MdTableBody(TypedDict):
    type: Literal["table_body"]
    children: list[MdTableBodyRow]


class MdTable(TypedDict):
    type: Literal["table"]
    children: list[MdTableHead | MdTableBody]


class MdInlineHTML(TypedDict):
    type: Literal["inline_html"]
    text: str


class MdInlineKeyboard(TypedDict):
    type: Literal["kbd"]
    text: str


type TMdTypes = (
    MdListItem
    | MdListUnordered
    | MdListOrdered
    | MdBlockCode
    | MdThematicBreak
    | MdNewLine
    | MdLineBreak
    | MdCodeSpan
    | MdBlockText
    | MdBlockQuote
    | MdBlockHTML
    | MdText
    | MdTextStrong
    | MdTextEmphasis
    | MdHeading
    | MdTableBodyCell
    | MdTableBodyRow
    | MdTableHead
    | MdTableBody
    | MdTable
    | MdTableHeadCell
    | MdParagraph
    | MdLink
    | MdImage
    | MdInlineHTML
    | MdInlineKeyboard
)

type TMdDocument = list[TMdTypes]

# Nested block containers parse with `list_rules`/`block_quote_rules`, snapshots of
# the core rule names taken before plugins append to `md.block.rules`. `MdTable` is
# therefore unreachable, and `MdListItem` only ever hangs off a list, never a peer.
type TMdBlockChildTypes = (
    MdNewLine
    | MdThematicBreak
    | MdHeading
    | MdBlockCode
    | MdBlockText
    | MdBlockQuote
    | MdBlockHTML
    | MdListOrdered
    | MdListUnordered
    | MdParagraph
)

type TMdInlineTypes = (
    MdCodeSpan
    | MdTextStrong
    | MdTextEmphasis
    | MdText
    | MdLineBreak
    | MdLink
    | MdImage
    | MdInlineHTML
    | MdInlineKeyboard
)

type TMdLinkChildTypes = (
    MdCodeSpan
    | MdTextStrong
    | MdTextEmphasis
    | MdText
    | MdLineBreak
    | MdImage
    | MdInlineHTML
    | MdInlineKeyboard
)
