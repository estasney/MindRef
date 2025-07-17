from __future__ import annotations

import abc
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Literal,
    Protocol,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from os import PathLike

    from mindref.lib.domain.editable import EditableNote
    from mindref.lib.domain.protocols import GetApp

    PLATFORM = Literal["win", "linux", "android", "macosx", "ios", "unknown"]


# noinspection PyUnusedLocal
class NoteRepositoryInitProtocol(Protocol):
    def __init__(
        self,
        get_app: GetApp,
        **kwargs,
    ): ...


class AbstractNoteRepository(ABC, NoteRepositoryInitProtocol):
    @property
    @abc.abstractmethod
    def configured(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def storage_path(self):
        raise NotImplementedError

    @storage_path.setter
    def storage_path(self, path: PathLike | None):
        raise NotImplementedError

    @abc.abstractmethod
    def discover_notes(self, on_complete: Callable) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def save_note(
        self,
        note: EditableNote,
        on_complete: Callable,
    ):
        raise NotImplementedError
