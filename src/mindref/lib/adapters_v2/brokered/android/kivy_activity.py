from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ActivityProtocol


@cache
def get_kivy_activity_cls() -> "type[ActivityProtocol]":
    from jnius import autoclass

    return autoclass("org.kivy.android.PythonActivity")


def get_kivy_activity() -> "ActivityProtocol":
    return get_kivy_activity_cls().mActivity
