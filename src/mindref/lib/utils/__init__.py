import os
from collections.abc import Callable

from functools import partial, wraps
from importlib.resources import files

from pathlib import Path
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    ClassVar,
    cast,
    override,
)

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder


if TYPE_CHECKING:
    from mindref.lib.domain.protocols import AppRegistryProtocol

_LOG_LEVEL = None

type ClockCallback = Callable[[float], object]


def required[T](value: T | None, message: str) -> T:
    """Type narrow Optional"""
    if value is None:
        raise RuntimeError(message)
    return value


def mindref_path() -> Path:
    return Path(str(files("mindref")))


def schedulable[**P](
    func: Callable[P, object], *args: P.args, **kwargs: P.kwargs
) -> ClockCallback:
    """
    Decorator to make a function schedulable with Kivy's Clock.

    Since Kivy insists on passing the time elapsed since the last frame, this decorator
    will ignore the first argument and pass the rest to the function.
    """

    @wraps(func)
    def scheduleable_inner(_dt: float) -> None:
        """This is the function that will be called by Kivy's Clock"""
        func(*args, **kwargs)

    return scheduleable_inner


def sch_cb(*callbacks: ClockCallback, timeout: float = 0) -> None:
    """
    Chain functions that sequentially call the next

    Passed to Clock to schedule
    """

    head_func = def_cb(*callbacks, timeout=timeout)
    Clock.schedule_once(head_func, timeout=timeout)


def def_cb(*callbacks: ClockCallback, timeout: float = 0) -> ClockCallback:
    """
    Chain functions that sequentially call the next

    Defers passing to clock to schedule

    Returns
    -------
    Returns a partial object that once called, starts a chain of events
    """

    func_pipe = iter(callbacks)

    def run_then_schedule_next(current: ClockCallback, dt: float) -> None:
        current(dt)
        next_func = next(func_pipe, None)
        if next_func is not None:
            cb = partial(run_then_schedule_next, next_func)
            Clock.schedule_once(cb, timeout)

    head_func = next(func_pipe, None)
    if head_func is None:
        return lambda _dt: None
    return partial(run_then_schedule_next, head_func)


def get_app() -> "AppRegistryProtocol":
    """Calls App.get_running_app() but casts as expected protocol"""
    from kivy.app import App

    return cast("AppRegistryProtocol", App.get_running_app())  # pyright: ignore[reportInvalidCast]


class EnvironContext:
    def __init__(self, vals: dict[str, str]):
        self.vals = vals

    def __enter__(self):
        import os

        for k, v in self.vals.items():
            os.environ[k] = v

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        for k in self.vals:
            del os.environ[k]


class Singleton(type):
    instances: ClassVar[dict[type, object]] = {}

    @override
    def __call__[T](cls: type[T], *args: object, **kwargs: object) -> T:
        if cls not in Singleton.instances:
            Singleton.instances[cls] = super().__call__(*args, **kwargs)
        return cast("T", Singleton.instances[cls])


class LazyLoaded[T]:
    def __init__(self, default: Callable[[], T] | None = None):
        self.default = default if default is None else default()
        self.private_name = ""
        self.loader = ""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.private_name = f"_{name}"
        setattr(owner, self.private_name, self.default)

    def __get__(self, obj: object, objtype: type[object] | None = None) -> T:
        value = getattr(obj, self.private_name)
        if value == self.default:
            value = getattr(obj, self.loader)()
            setattr(obj, self.private_name, value)
        return value

    def __set__(self, instance: object, value: T | None) -> None:
        if not value:
            setattr(instance, self.private_name, self.default)
        else:
            setattr(instance, self.private_name, value)

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Register a loader function"""
        self.loader = func.__name__
        return func
