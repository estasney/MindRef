from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from kivy.input.motionevent import MotionEvent
from kivy.uix.scrollview import ScrollView


class ScrollGesture(TypedDict):
    mode: Literal["unknown", "scroll"]
    dx: float
    dy: float
    user_stopped: bool
    frames: int
    time: float
    dt: NotRequired[float]


class SelectThroughScrollView(ScrollView):
    """ScrollView that passes mouse presses through to its children.

    It deviates from ScrollView behavior in that it does not claim exclusive
    judgment on whether a touch is a scroll based solely on it's own do_scroll_x/y.
    """

    def on_scroll_start(
        self, touch: MotionEvent, check_children: bool = True
    ) -> bool | None:
        if "button" in touch.profile:
            if touch.button in ("scrollup", "scrolldown") and not self.do_scroll_y:
                return False
            if touch.button in ("scrollleft", "scrollright") and not self.do_scroll_x:
                return False
        return super().on_scroll_start(touch, check_children)

    def on_scroll_move(self, touch: MotionEvent) -> bool | None:
        handled = super().on_scroll_move(touch)
        uid = self._get_uid()
        gesture: ScrollGesture | None = touch.ud.get(uid)
        vertical = (
            gesture is not None
            and gesture["mode"] == "unknown"
            and "button" not in touch.profile
            and gesture["dy"] > self.scroll_distance
            and gesture["dy"] > gesture["dx"]
        )
        if not vertical:
            return handled
        if self.effect_x is not None:
            self.effect_x.cancel()
        del touch.ud[uid]
        # svavoid blocks re-claiming on later moves. A cleared _touch
        # disarms the pending timeout.
        touch.ud[self._get_uid("svavoid")] = True
        self._touch = None
        return False

    def on_touch_down(self, touch: MotionEvent) -> bool | None:
        if (
            self.collide_point(*touch.pos)
            and "button" in touch.profile
            and not touch.button.startswith("scroll")
            and not self.touch_in_bar(touch)
        ):
            return self.simulate_touch_down(touch)
        return super().on_touch_down(touch)

    def touch_in_bar(self, touch: MotionEvent) -> bool:
        if "bars" not in self.scroll_type:
            return False
        if self.hbar[1] < 1.0:
            distance = (
                touch.y - self.y - self.bar_margin
                if self.bar_pos_x == "bottom"
                else self.top - touch.y - self.bar_margin
            )
            if 0 <= distance <= self.bar_width:
                return True
        if self.vbar[1] < 1.0:
            distance = (
                self.right - touch.x - self.bar_margin
                if self.bar_pos_y == "right"
                else touch.x - self.x - self.bar_margin
            )
            if 0 <= distance <= self.bar_width:
                return True
        return False
