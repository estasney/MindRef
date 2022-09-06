from bisect import bisect
from collections import deque
from dataclasses import dataclass
from operator import attrgetter
from typing import Callable, Optional, cast

from kivy.metrics import dp
from kivy.properties import AliasProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


@dataclass
class Suggestion:
    title: str
    score: float
    index: int


class TypeAheadDropDown(DropDown):
    sel_idx = NumericProperty(defaultvalue=0)
    last_idx = NumericProperty(defaultvalue=0)
    max_suggestions = NumericProperty(defaultvalue=3)

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
        
    
    """

    __events__ = ("on_select", "on_dismiss", "on_items")
    _items_keys: Optional[list[float]]
    items_: deque[Suggestion]

    def __init__(self, **kwargs):
        super(TypeAheadDropDown, self).__init__(**kwargs)
        self.items_ = deque(maxlen=self.max_suggestions)
        self.items_score_getter_ = cast(
            attrgetter("score"), Callable[[Suggestion], float]
        )
        self._items_keys = None
        self._items_keys_expired = False
        self.register_event_type("on_items")
        self.item_widgets = []

    def get_items(self):
        return list(self.items_)

    def _compute_item_keys(self) -> list[float]:
        self._items_keys = sorted(
            [self.items_score_getter_(i) for i in self.items_], reverse=True
        )
        self._items_keys_expired = False
        return self._items_keys

    @property
    def items_keys(self):
        if self._items_keys:
            if self._items_keys_expired:
                return self._compute_item_keys()
            return self._items_keys
        return self._compute_item_keys()

    def add_item(self, item: Suggestion):
        item_idx = bisect(self.items_keys, self.items_score_getter_(item))
        if item_idx == 0:
            # Ignored
            return
        # Remove smallest if at maxlen
        self._items_keys_expired = True
        if self.items_.maxlen == len(self.items_):
            self.items_.popleft()
            item_idx -= 1
        if item_idx == 0:
            self.items_.appendleft(item)
            self.dispatch("on_items", self, self.items)
            return
        r = len(self.items_) - item_idx
        self.items_.rotate(r)
        self.items_.append(item)
        self.items_.rotate(-r)
        self.dispatch("on_items", self, self.items)

    def on_sel_idx(self, instance, val):
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
            self.sel_idx = max((self.sel_idx - 1), 0)
        else:
            self.sel_idx = min(self.max_suggestions, self.sel_idx + 1)

    def handle_select(self, idx):
        if idx is None:
            btn_text = self.ids.get(f"item-{self.sel_idx}").text
        else:
            btn_text = self.ids.get(idx).text

        return self.select(btn_text)

    def on_items(self, instance, items):
        for i, v in enumerate(items, start=1):
            child_key = f"item-{i}"
            child_v = self.ids.get(child_key)
            if not child_v:
                item_widget = Button(text=v, size_hint_y=None, height=dp(40))
                self.add_widget(item_widget)
                item_widget.fbind("on_release", lambda x: self.handle_select(child_key))
                self.ids[child_key] = item_widget
                continue
            child_v.text = v

    items = AliasProperty(get_items, setter=None)
