from collections.abc import Sequence
from functools import cache
from typing import TYPE_CHECKING

from mindref.lib import get_app
from mindref.lib.adapters.brokered.android.kivy_activity import get_kivy_activity

if TYPE_CHECKING:
    from mindref.lib.adapters.brokered.android.types import MindRefWindowInsetsProtocol

SIGNED_INT_RANGE = 1 << 32
SIGNED_INT_MAX = 1 << 31


@cache
def get_window_insets_cls() -> "type[MindRefWindowInsetsProtocol]":
    from jnius import autoclass

    return autoclass("org.estasney.android.MindRefWindowInsets")


def to_android_color(rgba: Sequence[float]) -> int:
    """Pack a Kivy RGBA colour into the signed ARGB integer Android expects.

    Full alpha overflows a signed Java int, so the value is wrapped rather than
    passed through as-is.
    """
    red, green, blue, alpha = (round(channel * 255) for channel in rgba)
    packed = (alpha << 24) | (red << 16) | (green << 8) | blue
    if packed >= SIGNED_INT_MAX:
        packed -= SIGNED_INT_RANGE
    return packed


def apply_window_insets() -> None:
    """Keep the UI clear of the system bars, and colour the edges they leave.

    Android 15 and later draw the status bar, navigation bar and display cutout
    over a window targeting SDK 35. Padding the activity's content view shrinks
    the SDL surface to the safe area, so Kivy lays out against a window that is
    already correct and needs no inset handling of its own.
    """
    background = to_android_color(get_app().colors["Dark"])
    get_window_insets_cls().applyToContentView(get_kivy_activity(), background)
