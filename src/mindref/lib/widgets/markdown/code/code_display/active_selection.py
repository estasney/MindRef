from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.input.motionevent import MotionEvent
from kivy.properties import BooleanProperty


class ActiveSelectionBehavior(EventDispatcher):
    """Grants an `active` state with window touch and key routing
    while active."""

    active = BooleanProperty(False)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.fbind("active", self.handle_active)

    def handle_active(self, instance: ActiveSelectionBehavior, value: bool) -> None:
        from kivy.core.window import Window

        if value:
            Window.bind(
                on_touch_down=self.route_window_touch,
                on_key_down=self.handle_window_key,
            )
        else:
            Window.unbind(
                on_touch_down=self.route_window_touch,
                on_key_down=self.handle_window_key,
            )

    def route_window_touch(self, window: object, touch: MotionEvent) -> bool:
        """Deactivate when a touch lands outside the widget."""
        if not self.selection_hit(touch):
            self.active = False
        return False

    def selection_hit(self, touch: MotionEvent) -> bool:
        """Whether a window-coordinate touch lands on the widget."""
        raise NotImplementedError("Mixins must implement selection_hit")

    def handle_window_key(
        self,
        window: object,
        key: int,
        scancode: int,
        codepoint: str | None,
        modifiers: list[str],
    ) -> bool:
        """Key input while active. Return True to consume."""
        return False
