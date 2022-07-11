from kivy import Logger
from kivy.clock import Clock
from kivy.properties import OptionProperty
from kivy.utils import QueryDict
from typing import Callable, TYPE_CHECKING, TypeVar, ParamSpec, Sequence
from functools import partial

from utils import DottedDict

if TYPE_CHECKING:
    from kivy.uix.widget import Widget

V = TypeVar("V")


def trigger_factory(
    target: "Widget", prop_name: str, values: Sequence[V]
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

    def trigger_runner(dt, prop, v):
        Logger.debug(f"{target}: {prop} --> {v}")
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
