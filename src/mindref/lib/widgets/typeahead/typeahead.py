from kivy import Logger
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.domain.events import TypeAheadQueryEvent
from mindref.lib.utils import attrsetter, get_app, import_kv, sch_cb
from mindref.lib.widgets.typeahead.typeahead_dropdown import (
    Suggestion,
    TypeAheadDropDown,
)

import_kv(__file__)


class TypeAhead(BoxLayout):
    """
    Logical Container for TypeAhead Widget
    """

    typer = ObjectProperty()
    min_query_length = NumericProperty(3)
    dd: TypeAheadDropDown | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dd = None
        get_app().bind(note_category=self.clear_text)

    def handle_text(self, _, val):
        if val and len(val) >= self.min_query_length:
            Logger.debug(f"TypeAhead: Query {val}")
            get_app().registry.push_event(
                TypeAheadQueryEvent(query=val, on_complete=self.handle_suggestions)
            )
        elif self.dd:
            self.dd.suggestions = []

    def clear_text(self, *_args):
        clear_text_ = attrsetter(self.typer, "text", "")
        sch_cb(clear_text_)

    def handle_scroll(self, val):
        if not self.dd:
            return True
        return self.dd.handle_scroll(val)

    def handle_select(self, *args, **kwargs):
        if kwargs.get("keyed"):
            Logger.debug("TypeAhead: Got Keyed Select")
            self.dd.handle_select(idx=None)
            return True
        instance, value = args
        Logger.debug(f"TypeAhead: Handle Select {value}")
        self.dd.dismiss()
        self.dd.unbind(on_select=self.handle_select)
        self.dd = None
        Logger.debug(f"TypeAhead: Selecting App Index {value.index}")

        app = get_app()

        def set_index(_dt):
            return app.select_index(value.index)

        sch_cb(self.clear_text, set_index, timeout=0.1)
        return None

    def handle_dismissed_dd(self, *_args):
        """Dropdown was dismissed ensure we reflect that"""
        if self.dd:
            self.dd.unbind(on_select=self.handle_select)
            self.dd = None

    def handle_suggestions(self, suggestions: list[Suggestion] | None):
        Logger.debug("TypeAhead: Handle Suggestions")
        if not self.dd:
            self.dd = TypeAheadDropDown()
            self.dd.bind(on_select=self.handle_select)
            self.dd.bind(on_dismiss=self.handle_dismissed_dd)
            self.dd.open(self.typer)
        if not suggestions:
            self.dd.suggestions = []
        else:
            self.dd.suggestions = suggestions
