import abc
from abc import ABC
from typing import Optional


class BackendProtocol(ABC):
    @abc.abstractmethod
    @property
    def categories(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def current_category(self):
        raise NotImplementedError

    @abc.abstractmethod
    def next_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def previous_note(self):
        raise NotImplementedError
