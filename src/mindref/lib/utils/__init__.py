import os
from collections.abc import Callable

from functools import partial, wraps

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
)

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder


if TYPE_CHECKING:
    from mindref.lib.domain.protocols import AppRegistryProtocol

_LOG_LEVEL = None

T = TypeVar("T")
P = ParamSpec("P")
K = TypeVar("K", bound=str)
V = TypeVar("V")


def required[T](value: T | None, message: str) -> T:
    if value is None:
        raise RuntimeError(message)
    return value


def mindref_path() -> Path:
    # find our module location
    return Path(__file__).parent.parent.resolve()


def import_kv(path: str | Path) -> None:
    base_path = Path(path).resolve()
    kv_path = base_path.with_suffix(".kv")
    if kv_path.exists() and (sp := str(kv_path)) not in Builder.files:
        Logger.debug(f"Loading {kv_path.name}")
        Builder.load_file(sp, rulesonly=True)


def schedulable[**P, T](
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> Callable[[float], T]:
    """
    Decorator to make a function schedulable with Kivy's Clock.

    Since Kivy insists on passing the time elapsed since the last frame, this decorator
    will ignore the first argument and pass the rest to the function.
    """

    @wraps(func)
    def scheduleable_inner(*_iargs: float) -> T:
        """This is the function that will be called by Kivy's Clock"""
        return func(*args, **kwargs)

    return scheduleable_inner


def sch_cb(*args: Callable[P, T], timeout: float = 0) -> None:
    """
    Chain functions that sequentially call the next

    Passed to Clock to schedule
    """

    head_func = def_cb(timeout=timeout, *args)
    Clock.schedule_once(head_func, timeout=timeout)


def def_cb(*args: Callable[P, T], timeout: float = 0) -> Callable[[], None]:
    """
    Chain functions that sequentially call the next

    Defers passing to clock to schedule

    Returns
    -------
    Returns a partial object that once called, starts a chain of events
    """

    func_pipe = (f for f in args)

    def _scheduled_func(*s_args: P.args, **kwargs: P.kwargs) -> None:
        func: Callable[P, T] = kwargs.pop("func")
        func(*s_args, **kwargs)
        next_func = next(func_pipe, None)
        if next_func:
            cb = partial(_scheduled_func, func=next_func)
            Clock.schedule_once(cb, timeout)

    return partial(_scheduled_func, func=next(func_pipe))


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

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k in self.vals:
            del os.environ[k]


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
            return cls.__instance
        return cls.__instance


class LazyLoaded(Generic[T]):
    def __init__(self, default: "Callable | None" = None):
        self.default = default if default is None else default()

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
        setattr(owner, self.private_name, self.default)

    def __get__(self, obj, objtype=None) -> "T":
        value = getattr(obj, self.private_name)
        if value == self.default:
            value = getattr(obj, self.loader)()
            setattr(obj, self.private_name, value)
        return value

    def __set__(self, instance, value):
        if not value:
            setattr(instance, self.private_name, self.default)
        else:
            setattr(instance, self.private_name, value)

    def __call__(self, func):
        """Register a loader function"""
        self.loader = func.__name__
        return func
