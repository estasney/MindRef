"""Hand-written stub for `kivy.effects.opacityscroll` (kivy 2.3.1)."""

from kivy.effects.dampedscroll import DampedScrollEffect

__all__ = ("OpacityScrollEffect",)

class OpacityScrollEffect(DampedScrollEffect):
    def on_overscroll(self, *args: object) -> None: ...
