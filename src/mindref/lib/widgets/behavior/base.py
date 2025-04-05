class CustomBehavior:
    """
    Base class for custom behaviors.

    Event types are
    """

    __custom_events__ = frozenset({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for event in self.__custom_events__:
            self.register_event_type(event)
