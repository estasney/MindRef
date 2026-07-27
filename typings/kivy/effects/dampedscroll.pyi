"""Hand-written stub for `kivy.effects.dampedscroll` (kivy 2.3.1)."""

from kivy.effects.scroll import ScrollEffect
from kivy.properties import BooleanProperty, NumericProperty

__all__ = ("DampedScrollEffect",)

class DampedScrollEffect(ScrollEffect):
    edge_damping: NumericProperty
    spring_constant: NumericProperty
    min_overscroll: NumericProperty
    round_value: BooleanProperty
    def update_velocity(self, dt: float) -> None: ...
    def on_value(self, *args: object) -> None: ...
    def on_overscroll(self, *args: object) -> None: ...
    def apply_distance(self, distance: float) -> None: ...
