from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    NumericProperty,
)
from kivy.uix.widget import Widget

Builder.load_string("""
<Separator>:
    color: app.colors['Dark']
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            pos: self.pos
            size: self.size

<HSeparator@Separator>:
    size_hint_y: None
    height: dp(2)

<VSeparator@Separator>:
    size_hint_x: None
    width: dp(4)
""")


class Separator(Widget):
    color = ColorProperty()


class HSeparator(Separator): ...


class VSeparator(Separator): ...
