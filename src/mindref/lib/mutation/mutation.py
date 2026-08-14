from __future__ import annotations

from collections.abc import Callable
from functools import partial

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import (
    AliasProperty,
    ObjectProperty,
    OptionProperty,
)

from mindref.lib.models import MutationStatus
from mindref.lib.utils import schedulable


class Mutation[**P, R](EventDispatcher):
    """
    Runs a callable and reports its progress through Kivy events and properties.

    Events
    ------
    on_mutate
        Before the operation runs. `status` becomes `pending`.
    on_success
        After the operation returns. Receives the return value as the keyword
        argument `result`. `status` becomes `success`.
    on_error
        After the operation raised. Receives the exception as the keyword
        argument `error`. `status` becomes `error`.
    on_resolved
        After the operation finishes, whether it returned or raised.

    Properties
    ----------
    status
        MutationStatus - `idle`, `pending`, `success`, or `error`.
    exception
        The exception, or `None`. Set before `on_error` dispatches, so a handler
        can read it. Cleared by `reset` and by `on_success`.
    is_mutating
        True while `status` is `pending`. Bind this in KV to drive a spinner or
        to disable a control.
    error_message
        `exception` formatted for display, as `"TypeName: detail"`. Empty when
        there is no exception.

    Examples
    --------
    Wrap a method and bind to the events:

    >>> class SaveButton(LabelButton, LoadingButtonMixin):
    ...     def __init__(self, **kwargs: object):
    ...         super().__init__(**kwargs)
    ...         self.mutation = Mutation(self.save)
    ...         self.mutation.bind(
    ...             on_mutate=self.handle_on_mutate,
    ...             on_resolved=self.handle_on_resolved,
    ...         )
    ...
    ...     def save(self) -> None:
    ...         self.app.save_edit_note()

    Arguments pass through to the operation:

    >>> rename = Mutation(store.rename_note)
    >>> rename("note-1", "New title")

    In KV, bind to `is_mutating` rather than to `status`::

        <SaveButton>:
            disabled: self.mutation.is_mutating
    """

    status: OptionProperty[MutationStatus] = OptionProperty(
        MutationStatus.idle, options=tuple(MutationStatus)
    )
    exception: ObjectProperty[Exception | None] = ObjectProperty(allownone=True)
    operation: Callable[P, R]

    __events__ = ("on_mutate", "on_resolved", "on_success", "on_error")

    def __init__(self, operation: Callable[P, R]) -> None:
        super().__init__()
        self.operation = operation

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.reset()
        Clock.schedule_once(self.dispatch_on_mutate)
        Clock.schedule_once(schedulable(self._run, *args, **kwargs))

    def _get_is_mutating(self) -> bool:
        return self.status == MutationStatus.pending

    is_mutating: AliasProperty[bool] = AliasProperty(
        _get_is_mutating, rebind=True, bind=["status"]
    )

    def _get_error_message(self) -> str:
        if self.exception is None:
            return ""
        name = type(self.exception).__name__
        detail = str(self.exception)
        return f"{name}: {detail}" if detail else name

    error_message: AliasProperty[str] = AliasProperty(
        _get_error_message, rebind=True, bind=["exception"]
    )

    def dispatch_on_mutate(self, _dt: float) -> None:
        self.dispatch("on_mutate")

    def reset(self, *_args: object) -> None:
        """Reset the mutation to its initial state."""
        self.status = MutationStatus.idle
        self.exception = None

    def on_mutate(self, *_args: object) -> bool:
        self.status = MutationStatus.pending
        return True

    def on_success(self, *, result: R) -> bool:
        """Fired on the main thread when work finishes successfully."""
        self.exception = None
        self.status = MutationStatus.success
        return True

    def on_resolved(self, *_args: object) -> bool:
        """Dispatched regardless of error or success"""
        return True

    def on_error(self, *, error: Exception) -> bool:
        self.status = MutationStatus.error
        Logger.error(f"{type(self).__name__}: on_error - {error}")
        return True

    def dispatch_on_success(self, result: R, _dt: float) -> None:
        self.dispatch("on_success", result=result)

    def dispatch_on_resolved(self, _dt: float) -> None:
        self.dispatch("on_resolved")

    def _run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        try:
            result: R = self.operation(*args, **kwargs)
            Logger.debug(
                f"{type(self).__name__}: _run - mutation completed successfully with result: {result}"
            )
        except Exception as e:
            Logger.exception(
                f"{type(self).__name__}: _run - mutation failed with error"
            )

            self.exception = e
            self.dispatch("on_error", error=e)
        else:
            Clock.schedule_once(partial(self.dispatch_on_success, result))
        finally:
            Clock.schedule_once(self.dispatch_on_resolved)
