from __future__ import annotations

import re
from typing import Any

from mistune import InlineParser, Markdown

KBD_PATTERN = "(?:<kbd>)(.+?)(?:</kbd>)"


def parse_kbd(
    _inline: InlineParser, m: re.Match[str], _state: dict[str, Any]
) -> tuple[str, str]:
    text = m.group(1)
    return "kbd", text


def render_kbd(text: str) -> dict[str, str]:
    return {"type": "kbd", "text": text}


def plugin_kbd[TDocument](md: Markdown[TDocument]) -> None:
    md.inline.register_rule("kbd", KBD_PATTERN, parse_kbd)
    md.inline.rules.insert(1, "kbd")

    if md.renderer.NAME == "ast":
        md.renderer.register("kbd", render_kbd)
