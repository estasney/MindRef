from kivy.uix.widget import Widget


class InteractBehavior(Widget):
    """
    Mixin class that adds custom event 'on_interact'
    This fires when 'on_touch_down' is received and defers to super
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_interact")

    def on_interact(self): ...

    def on_touch_down(self, touch):
        self.dispatch("on_interact")
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.dispatch("on_interact")
        return super().on_touch_move(touch)
