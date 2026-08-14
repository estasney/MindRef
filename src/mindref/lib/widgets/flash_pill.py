from __future__ import annotations

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.label import Label

Builder.load_string("""
<FlashPill>:
    background_color: app.colors['Dark']
    font_size: sp(app.base_font_size - 2)
    size_hint: None, None
    size: self.texture_size
    padding: dp(12), dp(6)
    opacity: 0
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]
""")


class FlashPill(Label):
    """A pill label that fades in centered above the window bottom,
    holds, fades out, and unmounts itself."""

    background_color = ColorProperty()
    bottom_offset = NumericProperty("48dp")
    fade_in_duration = NumericProperty(0.1)
    hold_duration = NumericProperty(0.5)
    fade_out_duration = NumericProperty(0.2)

    def __init__(self, **kwargs: object) -> None:
        """Render the texture now, so size is valid before the first
        flash places the widget by it."""
        super().__init__(**kwargs)
        self.texture_update()

    def flash(self) -> None:
        from kivy.core.window import Window

        self.dismiss()
        self.center_x = Window.width / 2
        self.y = self.bottom_offset
        Window.add_widget(self, canvas="after")
        fade = (
            Animation(opacity=1.0, duration=self.fade_in_duration)
            + Animation(duration=self.hold_duration)
            + Animation(opacity=0.0, duration=self.fade_out_duration)
        )
        fade.bind(on_complete=self.dismiss)
        fade.start(self)

    def dismiss(self, *args: object) -> None:
        from kivy.core.window import Window

        Animation.cancel_all(self, "opacity")
        self.opacity = 0
        if self.parent is not None:
            Window.remove_widget(self)


__all__ = ["FlashPill"]
