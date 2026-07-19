from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import MindRefUtilsProtocol


@cache
def get_mindref_utils_cls() -> "type[MindRefUtilsProtocol]":
    from jnius import autoclass

    return autoclass("org.estasney.android.MindRefUtils")
