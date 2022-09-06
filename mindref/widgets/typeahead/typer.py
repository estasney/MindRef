from kivy.uix.textinput import TextInput

from utils import import_kv
from widgets.typeahead.typeahead_dropdown import TypeAheadDropDown

import_kv(__file__)


class TextTyper(TextInput):
    def __init__(self, **kwargs):
        super(TextTyper, self).__init__(**kwargs)
        self.dd = None
        self.register_event_type("on_suggestion_scroll")
        self.register_event_type("on_suggestion_select")

    def on_suggestion_scroll(self, val):
        self.dd.handle_scroll(val)

    def on_suggestion_select(self):
        self.dd.handle_select(None)

    def handle_select(self, instance, val):
        print(instance, val)
        self.dd = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        print(keycode, text, modifiers)
        if keycode[1] in {"down", "up"}:
            return self.dispatch("on_suggestion_scroll", keycode[1])
        elif keycode[1] == "enter":
            return self.dispatch("on_suggestion_select")
        super().keyboard_on_key_down(window, keycode, text, modifiers)

    def handle_text(self, instance, val):
        if self.dd and not val:
            self.dd.dismiss()
            self.dd = None
            return
        elif self.dd and val:
            self.dd.add_item(val)
            # self.dd.add_widget(Button(text=val, size_hint_y=None))
            return

        dd = TypeAheadDropDown()
        dd.add_item(val)
        # dd.add_widget(Button(text=val, size_hint_y=None, height=dp(18)))
        self.dd = dd
        dd.bind(on_select=self.handle_select)
        dd.open(self)
