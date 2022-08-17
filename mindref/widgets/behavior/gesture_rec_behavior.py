from kivy.uix.layout import Layout

from widgets.behavior.gestures import gdb, make_ud_gesture


class GestureRecognizingBehavior(Layout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gdb = gdb
        self.register_event_type("on_swipe")

    def do_layout(self, *args):
        super(GestureRecognizingBehavior, self).do_layout(*args)

    def on_touch_down(self, touch):
        super(GestureRecognizingBehavior, self).on_touch_down(touch)
        userdata = touch.ud
        userdata["points"] = [(touch.x, touch.y)]
        return True

    def on_touch_move(self, touch):
        super(GestureRecognizingBehavior, self).on_touch_move(touch)
        userdata = touch.ud
        userdata["points"] += [(touch.x, touch.y)]
        return True

    def on_touch_up(self, touch):
        # Convert to gesture and check for match
        gesture_obj = make_ud_gesture(touch)
        gesture_match = self.gdb.find(gesture_obj, minscore=0.8)
        if gesture_match:
            if gesture_match[1].name.startswith("swipe"):
                self.dispatch("on_swipe", *gesture_match)

    def on_swipe(self):
        ...
