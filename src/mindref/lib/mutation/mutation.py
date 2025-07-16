import threading
from collections.abc import Callable
from typing import Generic, Literal

from kivy import Logger
from kivy.clock import Clock, mainthread
from kivy.event import EventDispatcher
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    OptionProperty,
    StringProperty,
)
from typing_extensions import ParamSpec, TypeVar

from mindref.lib.models import MutationStatus

P = ParamSpec("P")
R = TypeVar("R")
TFn = Callable[P, R]


class Mutation(EventDispatcher, Generic[R]):
    status: MutationStatus = OptionProperty(
        MutationStatus.idle, options=MutationStatus.__members__.values()
    )
    error: str = StringProperty()

    __events__ = ("on_mutate", "on_resolved", "on_error", "on_success")
    _fn: TFn

    def __init__(self, fn: Callable[P, R]) -> None:
        super().__init__()
        self._fn = fn

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.reset()
        Clock.schedule_once(lambda *_: self.dispatch("on_mutate"))
        Clock.schedule_once(lambda *_: self._run(*args, **kwargs))

    def reset(self, *_):
        """Reset the mutation to its initial state."""
        self.status = MutationStatus.idle
        self.error = ""

    def _get_is_mutating(self):
        return self.status == MutationStatus.pending

    is_mutating: bool = AliasProperty(_get_is_mutating, rebind=True)

    def on_mutate(self, *_args) -> bool:
        self.status = MutationStatus.pending
        return True

    def on_success(self, *, result: R) -> bool:
        """Fired on the main thread when work finishes successfully."""
        self.error = ""
        self.status = MutationStatus.success
        return True

    def on_resolved(self, *_args) -> bool:
        """Dispatched regardless of error or success"""
        return True

    def on_error(self, *, err: Exception) -> bool:
        self.status = MutationStatus.error
        self.error = str(err)
        Logger.error(f"{type(self).__name__}: on_error - {self.error}")
        return True

    def _run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        try:
            result: R = self._fn(*args, **kwargs)
            Logger.debug(
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
        finally:
            Clock.schedule_once(lambda _dt: self.dispatch("on_resolved"))
