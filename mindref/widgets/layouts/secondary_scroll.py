from kivy.properties import BooleanProperty
from kivy.uix.scrollview import ScrollView


class SecondaryScroll(ScrollView):
    """
    This class is used primarily for the implementing a custom on_touch_move method.
    This method allows for use to forcibly release the touch event given a certain condition.

    Attributes
    ----------
    force_release: BooleanProperty
        If True, any touches that are grabbed will be released when on_touch_move is called.
    """

    force_release = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.force_release:
            touch.ungrab(self)
            return True
        return super().on_touch_move(touch)
