from datetime import datetime
from functools import wraps
from kivy.lang import Builder
from kivy import Logger

_LOG_LEVEL = None


def import_kv(path):
    import os

    base_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
    )
    kv_path = os.path.relpath(path, base_path).rsplit(".", 1)[0] + ".kv"
    if kv_path not in Builder.files:
        Builder.load_file(kv_path, rulesonly=True)


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
