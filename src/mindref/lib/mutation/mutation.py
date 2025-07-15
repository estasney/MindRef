import threading
from collections.abc import Callable
from typing import Generic

from kivy import Logger
from kivy.clock import Clock, mainthread
from kivy.event import EventDispatcher
from typing_extensions import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
TFn = Callable[P, R]


class Mutation(EventDispatcher, Generic[R]):
    __events__ = ("on_mutate", "on_resolved", "on_error", "on_success")
    _fn: TFn

    def __init__(self, fn: Callable[P, R]) -> None:
        super().__init__()
        self._fn = fn

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Start the mutation."""
        Logger.info(
            f"{type(self).__name__}: __call__ - starting mutation with args: {args}, kwargs: {kwargs}"
        )
        # 1. tell the UI were starting
        Clock.schedule_once(lambda *_: self.dispatch("on_mutate"))

        # 2. do the heavy work off the main thread
        threading.Thread(
            target=self._run, args=args, kwargs=kwargs, daemon=True
        ).start()

    def on_mutate(self, *_args) -> bool:
        """Fired on the main thread *before* work starts."""
        return False

    def on_success(self, *, result: R) -> bool:
        """Fired on the main thread when work finishes successfully."""
        return False

    def on_resolved(self, *_args) -> bool:
        """'Final' event fired on the main thread after work is done."""
        return False

    def on_error(self, *, err: Exception) -> bool:
        """Fired on the main thread if the work raises."""
        return False

    @mainthread
    def _run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Workhorse running in a background thread."""
        Logger.info(f"{type(self).__name__}: _run - running from thread")
        try:
            result: R = self._fn(*args, **kwargs)
            Logger.info(
                f"{type(self).__name__}: _run - mutation completed successfully with result: {result}"
            )
        except Exception as e:
            Logger.error(
                f"{type(self).__name__}: _run - mutation failed with error: {e}"
            )
            Clock.schedule_once(lambda _dt, err=e: self.dispatch("on_error", err=err))
        else:
            Logger.info(
                f"{type(self).__name__}: _run - mutation succeeded with result: {result}"
            )
            Clock.schedule_once(
                lambda _dt, res=result: self.dispatch("on_success", result=res)
            )
            Clock.schedule_once(lambda _dt: self.dispatch("on_resolved"))
