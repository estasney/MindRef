from functools import cache
from typing import TYPE_CHECKING

from .kivy_activity import get_kivy_activity

if TYPE_CHECKING:
    from .types import MindRefWindowInsetsProtocol


@cache
def get_window_insets_cls() -> "type[MindRefWindowInsetsProtocol]":
    from jnius import autoclass

    return autoclass("org.estasney.android.MindRefWindowInsets")


def apply_window_insets() -> None:
    """Keep the UI clear of the system bars.

    Android 15 and later draw the status bar, navigation bar and display cutout
    over a window targeting SDK 35. Padding the activity's content view shrinks
    the SDL surface to the safe area, so Kivy lays out against a window that is
    already correct and needs no inset handling of its own.
    """
    get_window_insets_cls().applyToContentView(get_kivy_activity())
