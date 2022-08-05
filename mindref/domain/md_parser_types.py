from __future__ import annotations
from typing import Literal, Optional, TypedDict, Union

TEXT = Literal["text"]
HEADING = Literal["heading"]
TABLE = Literal["table"]
TABLE_HEAD = Literal["table_head"]
TABLE_BODY = Literal["table_body"]
TABLE_ROW = Literal["table_row"]
TABLE_CELL = Literal["table_cell"]
TABLE_CELL_ALIGN = Optional[Literal["left", "right", "center"]]
STRONG = Literal["strong"]
EMPHASIS = Literal["emphasis"]
CODESPAN = Literal["codespan"]
LINEBREAK = Literal["linebreak"]
LINK = Literal["link"]
NEWLINE = Literal["newline"]
THEMATIC_BREAK = Literal["thematic_break"]
BLOCK_CODE = Literal["block_code"]
BLOCK_TEXT = Literal["block_text"]
BLOCK_QUOTE = Literal["block_quote"]
LIST = Literal["list"]
LIST_ITEM = Literal["list_item"]
PARAGRAPH = Literal["paragraph"]
INLINE_HTML = Literal["inline_html"]
INLINE_KBD = Literal["kbd"]

MD_LIT_TYPES = Union[
    TEXT,
    HEADING,
    TABLE,
    TABLE_HEAD,
    TABLE_BODY,
    TABLE_ROW,
    TABLE_CELL,
    TABLE_CELL_ALIGN,
    STRONG,
    CODESPAN,
    LINEBREAK,
    NEWLINE,
    THEMATIC_BREAK,
    BLOCK_CODE,
    BLOCK_TEXT,
    LIST,
    LIST_ITEM,
    PARAGRAPH,
    LINK,
    INLINE_HTML,
    INLINE_KBD,
]


class MdLinkItem(TypedDict):
    type: LINK
    link: str
    children: Optional[MdText]
    title: Optional[str]


class MdListItem(TypedDict):
    type: LIST_ITEM
    children: list[MD_TYPES]
    level: int


class MdListUnordered(TypedDict):
    type: LIST
    children: list[MdListItem]
    ordered: Literal[False]
    level: int


class MdListOrdered(TypedDict):
    type: LIST
    children: list[MdListItem]
    ordered: Literal[True]
    level: int


class MdBlockCode(TypedDict):
    type: BLOCK_CODE
    text: str
    info: Optional[str]


class MdThematicBreak(TypedDict):
    type: THEMATIC_BREAK


class MdNewLine(TypedDict):
    type: NEWLINE


class MdLineBreak(TypedDict):
    type: LINEBREAK


class MdCodeSpan(TypedDict):
    type: CODESPAN
    text: str


class MdBlockQuote(TypedDict):
    type: BLOCK_QUOTE
    children: list[MD_TYPES]


class MdBlockText(TypedDict):
    type: MdBlockText
    children: list[MD_TYPES]


class MdText(TypedDict):
    type: TEXT
    text: str


class MdTextEmphasis(TypedDict):
    type: EMPHASIS
    children: list[MdText]


class MdTextStrong(TypedDict):
    type: STRONG
    children: list[MdText]


class MdHeading(TypedDict):
    type: HEADING
    children: list[MD_TYPES]
    level: int


class MdParagraph(TypedDict):
    type: PARAGRAPH
    children: list[MD_TYPES]


class MdTableBodyCell(TypedDict):
    type: TABLE_CELL
    children: list[MD_TYPES]
    align: TABLE_CELL_ALIGN
    is_head: Literal[False]


class MdTableHeadCell(TypedDict):
    type: TABLE_CELL
    children: list[MD_TYPES]
    align: TABLE_CELL_ALIGN
    is_head: Literal[True]


class MdTableBodyRow(TypedDict):
    type: TABLE_ROW
    children: list[MdTableBodyCell]


class MdTableHead(TypedDict):
    type: TABLE_HEAD
    children: list[MdTableHeadCell]


class MdTableBody(TypedDict):
    type: TABLE_BODY
    children: list[MdTableBodyRow]


class MdTable(TypedDict):
    type: TABLE
    children: list[Union[MdTableHead, MdTableBody]]


class MdInlineHTML(TypedDict):
    type: INLINE_HTML
    text: str


class MdInlineKeyboard(TypedDict):
    type: INLINE_KBD
    text: str


MD_TYPES = Union[
    MdListItem,
    MdListUnordered,
    MdListOrdered,
    MdBlockCode,
    MdThematicBreak,
    MdNewLine,
    MdLineBreak,
    MdCodeSpan,
    MdBlockText,
    MdBlockQuote,
    MdText,
    MdTextStrong,
    MdHeading,
    MdTableBodyCell,
    MdTableBodyRow,
    MdTableHead,
    MdTableBody,
    MdTable,
    MdTableHeadCell,
    MdParagraph,
    MdInlineHTML,
    MdKeyboard,
]

MD_DOCUMENT = list[MD_TYPES]

MD_LIT_BLOCK_TYPES = Union[
    NEWLINE,
    THEMATIC_BREAK,
    HEADING,
    BLOCK_CODE,
    BLOCK_QUOTE,
    BLOCK_TEXT,
    LIST,
    LIST_ITEM,
    PARAGRAPH,
]

MD_BLOCK_TYPES = Union[
    MdNewLine,
    MdThematicBreak,
    MdHeading,
    MdBlockCode,
    MdBlockText,
    MdBlockQuote,
    MdListOrdered,
    MdListUnordered,
    MdListItem,
    MdParagraph,
]

MD_LIT_INLINE_TYPES = Union[CODESPAN, STRONG, TEXT, EMPHASIS, INLINE_HTML, INLINE_KBD]

MD_INLINE_TYPES = Union[
    MdCodeSpan, MdTextStrong, MdText, MdTextEmphasis, MdInlineHTML, MdInlineKeyboard
]
