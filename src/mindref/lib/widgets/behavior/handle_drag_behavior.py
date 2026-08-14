from __future__ import annotations

from kivy.input.motionevent import MotionEvent

from mindref.lib.widgets.behavior.base import CustomBehavior


class HandleDragBehavior(CustomBehavior):
    """
    Mixin class that adds the drag events of a grab handle:
    'on_handle_pressed', 'on_handle_moved', 'on_handle_released'.

    The widget mixing this in supplies collide_point for its grip.
    A touch inside the grip is grabbed and consumed. Every position
    of the drag is reported through on_handle_moved in the parent's
    coordinate space. For a child of the window that space is window
    coordinates.
    """

    __events__ = ("on_handle_pressed", "on_handle_moved", "on_handle_released")

    def on_touch_down(self, touch: MotionEvent) -> bool | None:
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        touch.grab(self)
        self.dispatch("on_handle_pressed")
        return True

    def on_touch_move(self, touch: MotionEvent) -> bool | None:
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        self.dispatch("on_handle_moved", float(touch.x), float(touch.y))
        return True

    def on_touch_up(self, touch: MotionEvent) -> bool | None:
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        touch.ungrab(self)
        self.dispatch("on_handle_released")
        return True

    def on_handle_pressed(self) -> None:
        """
        Called when a touch lands on the grip. No drag has happened yet.
        """

    def on_handle_moved(self, x: float, y: float) -> None:
        """
        Called for each position of the grabbed touch.

        x, y: float
            The touch position in the parent's coordinate space.
        """

    def on_handle_released(self) -> None:
        """
        Called when the grabbed touch lifts.
        """


__all__ = ["HandleDragBehavior"]
