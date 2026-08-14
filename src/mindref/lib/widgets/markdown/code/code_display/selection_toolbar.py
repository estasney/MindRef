from __future__ import annotations

from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label

Builder.load_string("""
<SelectionToolbar>:
    text: "Copy"
    font_size: sp(app.base_font_size - 2)
    size_hint: None, None
    size: self.texture_size
    padding: dp(12), dp(6)
    canvas.before:
        Color:
            rgba: app.colors['CodeToolbar']
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]
""")


class SelectionToolbar(ButtonBehavior, Label):
    """The floating Copy button of an active selection."""

    def __init__(self, **kwargs: object) -> None:
        """Render the texture now, so size is valid before the first
        mount places the widget by it."""
        super().__init__(**kwargs)
        self.texture_update()


__all__ = ["SelectionToolbar"]
