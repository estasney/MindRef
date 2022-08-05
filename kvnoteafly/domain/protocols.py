from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Protocol, TypeVar

from service.registry import Registry


class AppRegistryProtocol(Protocol):
    registry: "Registry"


T = TypeVar("T", bound=AppRegistryProtocol)
GetApp = Callable[[], T]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Optional[Path]
    notes: list[Path]
