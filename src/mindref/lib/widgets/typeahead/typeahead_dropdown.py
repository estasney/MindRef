from collections.abc import Callable
from dataclasses import dataclass

from kivy import Logger
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.dropdown import DropDown
from kivy.weakproxy import WeakProxy

from mindref.lib.utils import import_kv
from mindref.lib.widgets.buttons.buttons import ThemedButton

import_kv(__file__)


@dataclass
class Suggestion:
    title: str
    index: int


class SuggestionButton(ThemedButton):
    index = NumericProperty()
    text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TypeAheadDropDown(DropDown):
    sel_idx = NumericProperty(defaultvalue=0)
    last_idx = NumericProperty(defaultvalue=0)
    max_suggestions = NumericProperty(defaultvalue=3)
    suggestions = ListProperty()

    """
    Custom Dropdown that implements search suggestions
    
    Attributes
    ----------
    sel_idx : NumericProperty
        When 0, indicates that no suggestion is selected. Otherwise
    last_idx: NumericProperty
        Last idx selected
    max_suggestions: NumericProperty
        The maximum number of suggestions to show
    suggestion_idx: DictProperty
        Lookup suggestion object from physical index
        
    
    """

    __events__ = ("on_select", "on_dismiss")
    items_score_getter_: Callable[[Suggestion], float]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_sel_idx(self, *_args):
        if self.last_idx > 0:
            last_key = f"item-{self.last_idx}"
            child_btn = self.ids.get(last_key)
            child_btn.state = "normal"
        if self.sel_idx > 0:
            sel_key = f"item-{self.sel_idx}"
            child_btn = self.ids.get(sel_key)
            child_btn.state = "down"

    def handle_scroll(self, val):
        self.last_idx = self.sel_idx
        if val == "up":
            self.sel_idx = max((self.sel_idx - 1), -1)
        else:
            self.sel_idx = min(self.max_suggestions, self.sel_idx + 1)
        Logger.debug(f"Idx: {self.sel_idx}, last: {self.last_idx}")

    def handle_select(self, *_args, **kwargs):
        idx = kwargs.get("idx")
        if idx is None:
            idx = self.sel_idx

        # We're given physical index, look up corresponding note index from selected widget
        item_widget = self.ids[f"item-{idx}"]
        matched_suggestion = Suggestion(title=item_widget.text, index=item_widget.index)
        return self.select(matched_suggestion)

    def on_suggestions(self, _instance, suggestions: list[Suggestion]):
        """We maintain an index wrt the note's position in the category and the physical index, in case we need to do
        something like, "select the 3rd button"
        """

        # Try to recycle suggestion button widgets, creating / destroying as needed to accommodate number of suggestions
        n_suggest = min(len(suggestions), self.max_suggestions)
        Logger.debug(f"Dropdown: {n_suggest} Suggestions")

        for i in range(1, self.max_suggestions + 1):
            # Use 1 indexed
            child_widget_key = f"item-{i}"
            if i >= n_suggest + 1 and child_widget_key in self.ids:
                # We have more buttons than needed
                item_widget = self.ids[child_widget_key]
                item_widget.funbind("on_release", self.handle_select, idx=i)
                self.remove_widget(item_widget)
                del self.ids[child_widget_key]
                Logger.debug(f"Removed {child_widget_key}")
            elif i < n_suggest + 1 and child_widget_key not in self.ids:
                # We create a button
                item_widget = SuggestionButton(text="", size_hint_y=None, height=dp(40))
                item_widget.fbind("on_release", self.handle_select, idx=i)
                item_proxy = WeakProxy(item_widget)
                self.add_widget(item_widget)
                self.ids[child_widget_key] = item_proxy
                Logger.debug(f"Added {child_widget_key}")

        for i, suggestion in enumerate(suggestions[: self.max_suggestions], start=1):
            # Pick the corresponding physical key for button
            child_widget_key = f"item-{i}"
            item_widget = self.ids[child_widget_key]
            item_widget.text = suggestion.title
            item_widget.index = suggestion.index
