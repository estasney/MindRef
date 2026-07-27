"""Hand-written stub for `kivy.effects.scroll` (kivy 2.3.1)."""

from kivy.effects.kinetic import KineticEffect
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget

__all__ = ("ScrollEffect",)

class ScrollEffect(KineticEffect):
    drag_threshold: NumericProperty
    min: NumericProperty
    max: NumericProperty
    scroll: NumericProperty
    overscroll: NumericProperty
    target_widget: ObjectProperty[Widget | None]
    displacement: NumericProperty
    def reset(self, pos: float) -> None: ...
    def on_value(self, *args: object) -> None: ...
    def start(self, val: float, t: float | None = None) -> None: ...
    def update(self, val: float, t: float | None = None) -> None: ...
    def stop(self, val: float, t: float | None = None) -> None: ...
