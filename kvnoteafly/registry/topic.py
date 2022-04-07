import functools
from typing import Any, Callable

from registry import DottedList, Publisher


class Topic(Publisher):
    def __call__(self, func: Callable[[Any], Any]):
        @functools.wraps(func)
        def publish_result(*args, **kwargs):
            result = func(*args, **kwargs)
            self.notify(result)

        return publish_result

    def __init__(self, name: str):
        super().__init__(name)


class TopicCollection:

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
        self.wrapper_name = f"{self.private_name}_wrapper"
        setattr(owner, f"_{name}_wrapper", DottedList("name"))

    def __get__(self, obj, objtype=None) -> list:
        result = getattr(obj, self.wrapper_name)
        return result

    def __set__(self, obj, value):
        if not value:
            setattr(obj, self.wrapper_name, DottedList("name"))
        else:
            setattr(obj, self.wrapper_name, DottedList("name", value))
