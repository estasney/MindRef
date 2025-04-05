from typing import TYPE_CHECKING

from . import CustomBehavior

if TYPE_CHECKING:
    from kivy.uix.widget import Widget


class V2RefreshBehavior(CustomBehavior):
    """
    Mixin class that adds custom event 'on_refresh'
    """

    __custom_events__ = frozenset({"on_refresh"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_refresh(self, widget: "Widget", state: bool):
        """
        Called when the refresh state changes
        state: bool
            True, when the refresh is triggered
            False, when the refresh is not triggered
        """
        ...


__all__ = ["V2RefreshBehavior"]
