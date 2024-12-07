import abc

from mindref.lib.adapters.notes.fs.fs_note_repository import FileSystemNoteRepository
from mindref.lib.adapters.notes.note_repository import AbstractNoteRepository


class AbstractUnitOfWork(abc.ABC):
    """Orchestrates entry and exit of note actions"""

    repo: AbstractNoteRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class FileSystemUnitOfWork(AbstractUnitOfWork):
    def __init__(self, repo: FileSystemNoteRepository):
        self.repo = repo

    def _commit(self):
        pass

    def rollback(self):
        pass
