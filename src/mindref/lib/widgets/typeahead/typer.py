from kivy.uix.textinput import TextInput

from mindref.lib.utils import import_kv

import_kv(__file__)


class TextTyper(TextInput):
    """
    Intended to be wrapped with TypeAhead

    Adds additional methods for suggestions
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_suggestion_scroll")
        self.register_event_type("on_suggestion_select")

    def on_suggestion_scroll(self, val): ...

    def on_suggestion_select(self, *args, **kwargs): ...

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] in {"down", "up"}:
            return self.dispatch("on_suggestion_scroll", keycode[1])
        if keycode[1] == "enter":
            return self.dispatch("on_suggestion_select")
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        return None
