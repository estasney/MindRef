from typing import Optional

from kivy import Logger
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from domain.events import TypeAheadQueryEvent
from utils import import_kv, sch_cb
from widgets.typeahead.typeahead_dropdown import Suggestion, TypeAheadDropDown

import_kv(__file__)


class TypeAhead(BoxLayout):
    """
    Logical Container for TypeAhead Widget
    """

    typer = ObjectProperty()
    min_query_length = NumericProperty(3)
    dd: Optional[TypeAheadDropDown]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dd = None

    def handle_text(self, instance, val):
        if val and len(val) >= self.min_query_length:
            Logger.debug(f"TypeAhead: Query {val}")
            App.get_running_app().registry.push_event(
                TypeAheadQueryEvent(query=val, on_complete=self.handle_suggestions)
            )
        elif self.dd:
            self.dd.suggestions = []

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

        app = App.get_running_app()
        clear_text = lambda dt: setattr(self.typer, "text", "")
        set_index = lambda dt: app.select_index(value.index)

        sch_cb(0.1, clear_text, set_index)

    def handle_dismissed_dd(self, *args, **kwargs):
        """Dropdown was dismissed ensure we reflect that"""
        self.dd.unbind(on_select=self.handle_select)
        self.dd = None

    def handle_suggestions(self, suggestions: Optional[list[Suggestion]]):
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
