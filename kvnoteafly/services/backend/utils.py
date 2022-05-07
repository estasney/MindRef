from typing import TYPE_CHECKING

import marko.inline

if TYPE_CHECKING:
    from marko.block import BlockElement


def get_md_node_text(node: "BlockElement"):
    if node is marko.inline.LineBreak:
        return "\n"
    if not hasattr(node, "children"):
        return ""
    if isinstance(node.children, str):
        return node.children
    if len(node.children) > 1:
        return " ".join([get_md_node_text(c) for c in node.children])

    return get_md_node_text(node.children[0])
