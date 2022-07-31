from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Protocol, TypeVar

from service.registry import Registry

T = TypeVar("T")


class AppRegistryProtocol(Protocol[T]):
    registry: "Registry"


GetApp = Callable[[], AppRegistryProtocol[T]]


class NoteDiscoveryProtocol(Protocol):
    category: str
    image_path: Optional[Path]
    notes: list[Path]
