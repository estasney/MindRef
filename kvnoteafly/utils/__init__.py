import os
from datetime import datetime
from functools import wraps
from typing import Union

from kivy.lang import Builder
from kivy import Logger
from pathlib import Path

_LOG_LEVEL = None


def import_kv(path: Union[Path, str]):
    base_path = Path(path).resolve()
    kv_path = base_path.with_suffix(".kv")
    if kv_path.exists() and (sp := str(kv_path)) not in Builder.files:
        Logger.info(f"Loading {kv_path.name}")
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
