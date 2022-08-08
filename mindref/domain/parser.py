import mistune
from typing import TYPE_CHECKING

from utils import Singleton

if TYPE_CHECKING:
    from .md_parser_types import MD_DOCUMENT, MD_TYPES


class MarkdownParser(metaclass=Singleton):
    _parser: mistune.Markdown

    def __init__(self):
        self._parser = mistune.create_markdown(
            renderer=mistune.AstRenderer(), plugins=["table"]
        )

    def parse(self, text: str) -> "MD_DOCUMENT":
        result = self._parser(text)
        return result


def get_md_node_text(node: "MD_TYPES"):
    node_type = node["type"]
    if node_type == "text":
        return node["text"]
    if node_type in ("linebreak", "newline", "thematic_break"):
        return "\n"
    if node_type in ("block_code", "codespan"):
        return node["text"]
    if node_type == "strong":
        return f"[b]{node['children'][0]['text']}[/b]"
    if "children" not in node:
        return ""
    if "text" in node:
        return node["text"]

    else:
        return " ".join([get_md_node_text(c) for c in node["children"]])
