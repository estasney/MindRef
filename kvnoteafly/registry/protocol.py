import abc
from abc import ABC
from collections import UserList
from typing import Any, Callable, Iterable, Optional

Listener = Callable[[Any], Any]
Emitter = Callable[[Iterable[Listener], Any], Any]


class Publisher(ABC):

    """
    Metaclass that registers an emitter with 0 or more listeners
    """

    emitter: Emitter

    def __init__(self, name, emitter: Optional[Emitter] = None):
        """

        Parameters
        ----------
        name
        emitter
            If None, `self.emitter` will be a generic func that passes *args and **kwargs to all listeners
        """
        self.name: str = name
        self.emitter = emitter if emitter else self._default_emitter_factory()
        self.listeners: list[Listener] = []

    def _default_emitter_factory(self):
        def emitter(listeners, *args, **kwargs):
            for listener in listeners:
                listener(*args, **kwargs)

        return emitter

    def notify(self, *args, **kwargs) -> None:
        """
        Call `self.emitter(self.listeners, result)`

        Parameters
        ----------
        result

        """
        self.emitter(self.listeners, *args, **kwargs)

    def set_emitter(self, emitter: Optional[Emitter]):
        """
        Set emitter

        Parameters
        ----------
        emitter : Optional[Emitter]

        Returns
        -------

        """
        self.emitter = emitter

    def add_listener(self, cb: Listener):
        self.listeners.append(cb)

    @abc.abstractmethod
    def __call__(self, func: Callable[[Any], Any]):
        raise NotImplementedError


class DottedList(UserList):
    def __init__(self, key_name: str, initlist=None):
        super().__init__(initlist)
        self.key_name = key_name

    def __getattr__(self, name: str):
        try:
            return next(
                (item for item in self.data if getattr(item, self.key_name) == name)
            )
        except StopIteration:
            raise AttributeError(f"{name} does not exist")

    def __call__(self, name: str):
        return self.__getattr__(name)
