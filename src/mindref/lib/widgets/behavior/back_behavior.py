from __future__ import annotations

from typing import TYPE_CHECKING

from mindref.lib.widgets.behavior.base import CustomBehavior

if TYPE_CHECKING:
    from kivy.event import EventDispatcher


class BackBehavior(CustomBehavior):
    """
    Mixin class that adds custom event 'on_back'
    """

    __events__ = ("on_back",)

    def on_back(self, source: EventDispatcher) -> bool:
        """
        Called when a back action is requested.

        source: EventDispatcher
            The originator of the request, such as the Window for a hardware
            key or a widget for an on-screen control.

        Return True when the action was consumed, False to leave it for the
        application default.
        """
        return False


__all__ = ["BackBehavior"]
