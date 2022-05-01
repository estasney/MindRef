from typing import Callable, Optional, TYPE_CHECKING

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


class LazyLoaded:
    def __init__(self, default: Optional[Callable] = None):
        self.default = default if default is None else default()

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
        setattr(owner, self.private_name, self.default)

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.private_name)
        if value == self.default:
            value = getattr(obj, self.loader)()
            setattr(obj, self.private_name, value)
        return value

    def __set__(self, instance, value):
        if not value:
            setattr(instance, self.private_name, self.default)
        else:
            setattr(instance, self.private_name, value)

    def __call__(self, func):
        """Register a loader function"""
        self.loader = func.__name__
        return func
