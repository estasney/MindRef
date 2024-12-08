import atexit
import os
from collections.abc import Callable
from datetime import datetime
from functools import partial, wraps
from operator import itemgetter
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    Unpack,
)

from kivy import Logger
from kivy.clock import Clock
from kivy.lang import Builder

from .triggers import trigger_factory

if TYPE_CHECKING:
    from line_profiler import LineProfiler

    from mindref.lib.domain.protocols import AppRegistryProtocol

_LOG_LEVEL = None

T = TypeVar("T")
P = ParamSpec("P")
K = TypeVar("K", bound=str)
V = TypeVar("V")


_PROFILER: "LineProfiler | None" = None


def get_stats() -> None:
    global _PROFILER  # noqa: PLW0602
    if _PROFILER is None:
        print("No Profiler")
        return
    # noinspection PyUnresolvedReferences
    from io import StringIO

    fp = StringIO()

    _PROFILER.print_stats(stream=fp)
    stats = fp.getvalue()
    fp.close()
    print(stats)
    Path("profile.txt").write_text(stats)


def profile(func):
    global _PROFILER
    if _PROFILER is None:
        try:
            from line_profiler import LineProfiler

            _PROFILER = LineProfiler()
        except ImportError:
            return func

    _PROFILER.add_function(func)
    _PROFILER.enable_by_count()
    atexit.register(get_stats)
    return func


def mindref_path() -> Path:
    # find our module location
    return Path(__file__).parent.parent.resolve()


def import_kv(path: str | Path) -> None:
    base_path = Path(path).resolve()
    kv_path = base_path.with_suffix(".kv")
    if kv_path.exists() and (sp := str(kv_path)) not in Builder.files:
        Logger.debug(f"Loading {kv_path.name}")
        Builder.load_file(sp, rulesonly=True)


def log_run_time(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapped_log_run_time(*args: P.args, **kwargs: P.kwargs) -> T:
        start_time = datetime.utcnow()
        result = func(*args, **kwargs)
        end_time = datetime.utcnow()
        Logger.debug(f"Run Time {(end_time - start_time)}")
        return result

    return wrapped_log_run_time


def schedulable(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> Callable[P, T]:
    """
    Decorator to make a function schedulable with Kivy's Clock.

    Since Kivy insists on passing the time elapsed since the last frame, this decorator
    will ignore the first argument and pass the rest to the function.

    Internally, this decorator wraps the function in a partial that will ignore the first argument.
    """

    # Use typing.Concatenate to annotate that Kivy will call scheduleable_inner with our args, kwargs and the time elapsed

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


def attrsetter(instance: object, attr: str, value: Any) -> Callable[[], None]:
    """
    Set an attribute of an instance operator style
    Parameters
    ----------
    instance
    attr
    value
    """

    def attrsetter_inner(*_args: Any) -> None:
        setattr(instance, attr, value)

    return attrsetter_inner


def fmt_attrs(instance: object, *attr: Unpack[tuple[str]]) -> str:
    """
    Build a param string formatted for logging with form
    [attr=getattr(instance, attr)]

    Returns
    -------
    """
    params = ((a, getattr(instance, a)) for a in attr)
    fmt_params = (f"{a!s}={v!s}" for a, v in params if v)
    param_str = ", ".join(fmt_params)
    return f"[{param_str}]"


def fmt_items(instance: "SupportsGetItem", *attr) -> str:
    """
    Build a param string formatted for logging with form
    [key=item]

    Returns
    -------
    """
    keys, values = attr, itemgetter(*attr)(instance)
    params = ((k, v) for k, v in zip(keys, values, strict=True))
    fmt_params = (f"{k!s}={v!s}" for k, v in params if v)
    param_str = ", ".join(fmt_params)
    return f"[{param_str}]"


def get_app() -> "AppRegistryProtocol":
    """Calls App.get_running_app() but casts as expected protocol"""
    from kivy.app import App

    app: AppRegistryProtocol = App.get_running_app()
    return app


class SupportsGetItem(Protocol):
    def __getitem__(self, item): ...


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


class DottedDict(dict, Generic[K, V]):
    def __init__(self):
        super().__init__()

    def __getattr__(self, item: K) -> V:
        return self[item]

    def __setattr__(self, key: K, value: V):
        self.__setitem__(key, value)
