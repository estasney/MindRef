import os
from datetime import datetime
from functools import partial, wraps
from pathlib import Path
from typing import Union

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
