from jnius import autoclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mindref.lib.adapters.notes.android.annotations import (
        MindRefUtilsProtocol,
        ActivityProtocol,
    )


_MINDREF_UTILS_CLS = None
_KIVY_ACTIVITY_CLS = None


def _get_mindref_utils_cls() -> "type[MindRefUtilsProtocol]":
    global _MINDREF_UTILS_CLS
    if _MINDREF_UTILS_CLS is None:
        _MINDREF_UTILS_CLS = autoclass("org.estasney.android.MindRefUtils")
    return _MINDREF_UTILS_CLS  # type: ignore


def _get_kivy_activity_cls() -> "ActivityProtocol":
    global _KIVY_ACTIVITY_CLS
    if _KIVY_ACTIVITY_CLS is None:
        _KIVY_ACTIVITY_CLS = autoclass("org.kivy.android.PythonActivity")
    return _KIVY_ACTIVITY_CLS.mActivity  # type: ignore


def __getattr__(name: str):
    if name == "MindRefUtils":
        return _get_mindref_utils_cls()
    elif name == "KivyActivity":
        return _get_kivy_activity_cls()
    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")


__all__ = [  # noqa: F822
    "MindRefUtils",  # type: ignore
    "KivyActivity",  # type: ignore
]
