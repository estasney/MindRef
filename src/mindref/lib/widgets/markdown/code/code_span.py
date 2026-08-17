from __future__ import annotations

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments.style import Style
from pygments.token import Token

from mindref.lib.widgets.markdown.code.code_display.jetbrains_dark import JetBrainsDark
from mindref.lib.widgets.style import BaseLabel

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import styles mindref.lib.widgets.style

<MarkdownCodeSpan>:
    id: parent
    cols: 1
    size_hint_y: None
    height: self.minimun_height
    padding: (0, 0, 0, label.texture_size[1] * .1)
    canvas.before:
        Color:
            rgba: app.colors['Dark']
        Rectangle:
            pos: self.x - 1, self.y - 1
            size: self.width + 2, self.height + 2
        Color:
            rgba: parse_color(self.background_color)
        Rectangle:
            pos: self.pos
            size: self.size
    BaseLabel:
        id: content
        text: root.text
        markup: True
        size_hint: 0.99, 0.95
        mipmap: True
        text_size: self.size[0], None
        font_name: "JetBrainsMono"
        font_hinting: 'mono'
        padding_x: min(self.size[1] / 2), sp(16)
""")


class MarkdownCodeSpan(GridLayout):
    content: ObjectProperty[BaseLabel] = ObjectProperty()
    styler: ObjectProperty[type[Style]] = ObjectProperty(JetBrainsDark)
    raw_text = StringProperty()
    text = StringProperty()
    background_color = StringProperty()

    def __init__(self, text: str, **kwargs: object):
        super().__init__(**kwargs)
        self.background_color = self.styler.background_color
        self.raw_text = text

    def on_styler(self, _instance: object, new: type[Style]) -> None:
        self.background_color = new.background_color
        self.render_text()

    def on_raw_text(self, _instance: object, new: str) -> None:
        self.render_text()

    def render_text(self) -> None:
        """Wrap the raw text in a BBCode colour tag taken from the styler."""
        self.text = f"[color={self.styler.styles[Token.Text]}]{self.raw_text}[/color]"
