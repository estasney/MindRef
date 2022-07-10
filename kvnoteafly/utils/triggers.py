from kivy import Logger
from kivy.clock import Clock
from kivy.properties import OptionProperty
from kivy.utils import QueryDict
from typing import TYPE_CHECKING
from functools import partial

from utils import DottedDict

if TYPE_CHECKING:
    from kivy.uix.widget import Widget


def trigger_factory(target: "Widget", prop_name: str) -> DottedDict:
    """
    Generate functions for updating state and register them as triggers

    Returns
    -------
    """

    # We want to access the class definition and modify the instance definition

    cls_prop = getattr(target.__class__, prop_name)

    triggers = DottedDict()

    def trigger_inner(dt, prop, val):
        Logger.debug(f"Setting {prop} to {val}")
        setattr(target, prop_name, val)

    if isinstance(cls_prop, OptionProperty):
        for opt in cls_prop.options:

            f = partial(trigger_inner, prop=prop_name, val=opt)

            f_trigger = Clock.create_trigger(f)
            triggers[opt] = f_trigger
        return triggers
    else:
        raise NotImplementedError(f"Property {type(cls_prop)} is not handled")
