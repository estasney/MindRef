import os
from datetime import datetime
from functools import partial, wraps
from pathlib import Path
from typing import Any, Callable, Generic, Literal, Optional, Protocol, TypeVar, Union

from kivy import Logger
from kivy.clock import Clock
from kivy.lang import Builder


_LOG_LEVEL = None


def import_kv(path: Union[Path, str]):
    base_path = Path(path).resolve()
    kv_path = base_path.with_suffix(".kv")
    if kv_path.exists() and (sp := str(kv_path)) not in Builder.files:
        Logger.debug(f"Loading {kv_path.name}")
        Builder.load_file(sp, rulesonly=True)


def get_log_level():
    global _LOG_LEVEL
    if _LOG_LEVEL:
        return _LOG_LEVEL
    from kivy.app import App

    _LOG_LEVEL = App.get_running_app().log_level

    return _LOG_LEVEL


def log_run_time(func):
    @wraps(func)
    def wrapped_log_run_time(*args, **kwargs):
        start_time = datetime.utcnow()
        result = func(*args, **kwargs)
        end_time = datetime.utcnow()
        Logger.debug(f"Run Time {(end_time - start_time)}")
        return result

    return wrapped_log_run_time


def sch_cb(timeout: float = 0, *args):
    """Chain functions that sequentially call the next"""

    func_pipe = (f for f in args)

    def _scheduled_func(*args, **kwargs):
        func = kwargs.pop("func")
        func(*args, **kwargs)
        next_func = next(func_pipe, None)
        if next_func:
            cb = partial(_scheduled_func, func=next_func)
            Clock.schedule_once(cb, timeout)

    head_func = partial(_scheduled_func, func=next(func_pipe))

    Clock.schedule_once(head_func, timeout=timeout)


class EnvironContext:
    def __init__(self, vals: dict[str, str]):
        self.vals = vals

    def __enter__(self):
        import os

        for k, v in self.vals.items():
            os.environ[k] = v

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k in self.vals.keys():
            del os.environ[k]


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance
        else:
            return cls.__instance


T = TypeVar("T")


class LazyLoaded(Generic[T]):
    def __init__(self, default: "Optional[Callable]" = None):
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


class LoggerProtocol(Protocol):
    def debug(self, msg: Any):
        ...

    def info(self, msg: Any):
        ...

    def warning(self, msg: Any):
        ...

    def error(self, msg: Any):
        ...

    def exception(self, msg: Any):
        ...


LOG_LEVEL = Literal["debug", "info", "warning", "error", "exception"]


class GenericLoggerMixin:
    logger: Optional[LoggerProtocol]
    _log: Optional[Callable[[Any, LOG_LEVEL], None]]

    def __init__(self):

        self._log = None

    def log(self, msg: Any, level: LOG_LEVEL):
        if self._log:
            self._log(msg, level)
        # Create the method on the fly
        if self.logger:
            self._log = lambda msg, lvl: getattr(self.logger, lvl)(msg)
            self._log(msg, level)
        else:
            self._log = lambda msg, lvl: print(msg)
            self._log(msg, level)


K = TypeVar("K", bound=str)
V = TypeVar("V")


class DottedDict(dict, Generic[K, V]):
    def __init__(self):
        super().__init__()

    def __getattr__(self, item: K) -> V:

        return self[item]

    def __setattr__(self, key: K, value: V):
        self.__setitem__(key, value)
