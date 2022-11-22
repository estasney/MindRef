from functools import partial
from typing import Callable, Sequence, TYPE_CHECKING, TypeVar

from kivy import Logger
from kivy.clock import Clock

if TYPE_CHECKING:
    from kivy.event import EventDispatcher

V = TypeVar("V")


def trigger_factory(
    target: "EventDispatcher", prop_name: str, values: Sequence[V]
) -> Callable[[V], None]:
    """
    Generate functions for setting a property to a value

    Parameters
    ----------
    target
    prop_name
    values

    Returns
    -------

    """

    triggers = {}

    def trigger_runner(_dt, prop, v):
        if hasattr(target, "__class__"):
            Logger.debug(
                f"{target.__class__.__name__}: {prop} {getattr(target, prop_name)}--> {v}"
            )
        else:
            Logger.debug(f"{target}: {prop} {getattr(target, prop_name)}--> {v}")
        setattr(target, prop_name, v)

    def trigger_outer(value_set: V):
        """set prop to value_set"""
        func = triggers[value_set]
        func()

    for val in values:
        f = partial(trigger_runner, prop=prop_name, v=val)
        f_trigger = Clock.create_trigger(f)
        triggers[val] = f_trigger

    return trigger_outer
