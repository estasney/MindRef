from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.domain.md_parser_types import *


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
