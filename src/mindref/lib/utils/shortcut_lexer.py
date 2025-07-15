# shortcut_lexer.py
from __future__ import annotations

from typing import ClassVar

from pygments.lexer import RegexLexer
from pygments.token import Name, Operator, Whitespace


class ShortcutLexer(RegexLexer):
    """Minimal lexer for comma‑separated shortcut notation."""

    name = "Shortcut"
    aliases = ["shortcut"]
    filenames: ClassVar[list[str]] = []  # no automatic filename mapping

    tokens: ClassVar[dict] = {
        "root": [
            (r"\s+", Whitespace),  # allow arbitrary spacing
            (r",", Operator),  # the separator
            (r"[^,\s]+", Name.Constant),  # any non‑comma chunk
        ]
    }


try:
    from pygments.lexers import _mapping  # noqa

    _mapping.LEXERS["ShortcutLexer"] = (
        __name__,  # module path
        ShortcutLexer.name,  # display name
        tuple(ShortcutLexer.aliases),
        tuple(ShortcutLexer.filenames),
        ("text/x-shortcut",),  # optional MIME types
    )
except Exception:  # pragma: no cover
    pass

__all__ = ["ShortcutLexer"]
