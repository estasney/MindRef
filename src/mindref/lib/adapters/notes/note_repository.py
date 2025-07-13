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

    from ...domain.settings import SortOptions
    from .android.android_note_repository import AndroidNoteRepository
    from .fs.fs_note_repository import FileSystemNoteRepository

    PLATFORM = Literal["win", "linux", "android", "macosx", "ios", "unknown"]


# noinspection PyUnusedLocal
class NoteRepositoryInitProtocol(Protocol):
    def __init__(
        self,
        get_app: GetApp,
        **kwargs,
    ): ...


class NoteRepositoryFactory:
    @classmethod
    def _get_repo_android(cls) -> type[AndroidNoteRepository]:
        from .android.android_note_repository import AndroidNoteRepository

        return AndroidNoteRepository

    @classmethod
    def _get_repo_default(cls) -> type[FileSystemNoteRepository]:
        from .fs.fs_note_repository import FileSystemNoteRepository

        return FileSystemNoteRepository

    @classmethod
    def get_repo(cls) -> type[FileSystemNoteRepository] | type[AndroidNoteRepository]:
        """
        Dynamic Class returned based on platform.
        """

        from kivy import platform

        match platform:
            case "android":
                return cls._get_repo_android()
            case _:
                return cls._get_repo_default()


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
