from kivy.uix.widget import Widget


class RefreshBehavior(Widget):
    """
    Mixin class that adds custom event 'on_refresh'
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_refresh")

    def on_refresh(self, state: bool):
        ...
