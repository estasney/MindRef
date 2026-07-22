from typing import ClassVar

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Token,
    Whitespace,
)


class JetBrainsDark(Style):
    background_color = "#191A1C"
    highlight_color = "#214283"

    styles: ClassVar[dict] = {
        Token.Text: "#BCBEC4",
        Whitespace: "#BCBEC4",
        Error: "#F75464",
        Comment: "#7A7E85",
        Keyword: "#CF8E6D",
        Operator: "#BCBEC4",
        Operator.Word: "#CF8E6D",
        Punctuation: "#BCBEC4",
        Name: "#BCBEC4",
        Name.Function: "#56A8F5",
        Name.Class: "#BCBEC4",
        Name.Decorator: "#B3AE60",
        Name.Builtin.Pseudo: "#94558D",
        Number: "#2AACB8",
        String: "#6AAB73",
        String.Doc: "#5F826B",
        String.Escape: "#CF8E6D",
        String.Interpol: "#CF8E6D",
        Generic.Heading: "bold #BCBEC4",
        Generic.Subheading: "bold #BCBEC4",
        Generic.Emph: "italic #BCBEC4",
        Generic.Strong: "bold #BCBEC4",
        Generic.Deleted: "#F75464",
        Generic.Inserted: "#6AAB73",
        Generic.Error: "#F75464",
    }
