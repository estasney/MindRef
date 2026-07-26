from typing import TYPE_CHECKING

from kivy.logger import Logger

from mindref.lib.widgets.behavior import CustomBehavior

if TYPE_CHECKING:
    from kivy.uix.widget import Widget


class V2RefreshBehavior(CustomBehavior):
    """
    Mixin class that adds custom event 'on_refresh'
    """

    __events__ = ("on_refresh",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _find_closest_parent_handler(self) -> "Widget | None":
        """
        Find the closest parent widget that has an 'on_refresh' handler.
        """
        return next(
            (
                widget
                for widget in self.walk_reverse()
                if widget.is_event_type("on_refresh")
            ),
            None,
        )

    def on_refresh(self, widget: "Widget", state: bool, to_children: bool) -> bool:
        """
        Called when the refresh state changes
        state: bool
            True, when the refresh is triggered
            False, when the refresh is not triggered
        children: bool
            True, then propagate the event to children widgets
            False, propagate the event to parent widget
        """
        Logger.debug(
            f"{type(self).__name__} : on_refresh src='{widget.__class__.__name__}', {state=}, {to_children=}"
        )
        if to_children:
            return self.dispatch_children("on_refresh", widget, state, to_children)

        matched_parent = self._find_closest_parent_handler()
        if not matched_parent:
            Logger.debug(
                f"{self.__class__.__name__}: No parent with on_refresh handler found"
            )
            return False

        return matched_parent.dispatch("on_refresh", widget, state, to_children)


__all__ = ["V2RefreshBehavior"]
