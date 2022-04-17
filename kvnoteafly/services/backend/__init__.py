import abc
from abc import ABC
from typing import Optional


class BackendProtocol(ABC):
    @property
    @abc.abstractmethod
    def categories(self) -> list[str]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_category(self):
        raise NotImplementedError

    @abc.abstractmethod
    def next_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def previous_note(self):
        raise NotImplementedError
