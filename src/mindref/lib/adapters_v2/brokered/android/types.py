from collections.abc import Callable
from enum import IntEnum, auto
from typing import Protocol, runtime_checkable


class V2MindRefCallCodes(IntEnum):
    PROMPT_EXTERNAL_STORAGE = auto()
    IMPORT_EXTERNAL_STORAGE = auto()
    COPY_TO_EXTERNAL_STORAGE = auto()


@runtime_checkable
class UriProtocol(Protocol):
    getPath: Callable[[], str]
    getEncodedPath: Callable[[], str]
    isAbsolute: Callable[[], bool]
    getScheme: Callable[[], str]
    getAuthority: Callable[[], str]
    getPathSegments: Callable[[], list[str]]
    getLastPathSegment: Callable[[], str]
    toString: Callable[[], str]
    parse: Callable[[str], "UriProtocol"]
