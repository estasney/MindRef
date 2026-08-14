from __future__ import annotations

from kivy.core.text import Label as CoreLabel

type Cell = tuple[int, int]


class TextMeasurer:
    def __init__(self, font_name: str, font_size: float) -> None:
        self.label = CoreLabel(font_name=font_name, font_size=font_size)
        self.line_height = self.label.get_extents("Mg")[1]

    def width(self, text: str) -> float:
        return self.label.get_extents(text)[0]
