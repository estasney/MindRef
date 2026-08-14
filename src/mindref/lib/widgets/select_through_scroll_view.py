from __future__ import annotations

from kivy.input.motionevent import MotionEvent
from kivy.uix.scrollview import ScrollView


class SelectThroughScrollView(ScrollView):
    """ScrollView that passes mouse presses through to its children.

    ScrollView holds every touch to test for a scroll gesture, which keeps
    mouse drags from reaching children as text selection. Mouse presses go
    straight to the children; pointer scrolling stays available through the
    wheel and the scrollbars. Finger touches keep the scroll-first behavior.

    ScrollView also consumes wheel events on axes it cannot scroll, which
    blocks an enclosing ScrollView from acting on them. Those are declined.
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
