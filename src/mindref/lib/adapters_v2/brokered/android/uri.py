from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import UriProtocol


@cache
def get_uri_cls() -> "UriProtocol":
    from jnius import autoclass

    return autoclass("android.net.Uri")
