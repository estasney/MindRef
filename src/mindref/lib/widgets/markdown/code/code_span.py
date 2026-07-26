from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments.token import Token

from mindref.lib.widgets.markdown.code.jetbrains_dark import JetBrainsDark

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import styles mindref.lib.widgets.style

<MarkdownCodeSpan>:
    id: parent
    cols: 1
    size_hint_y: None
    height: content.texture_size[1] + dp(20)
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
        padding_x: min(sp(self.size[1] / 2), sp(16))
""")


class MarkdownCodeSpan(GridLayout):
    content = ObjectProperty()
    raw_text = StringProperty()
    text = StringProperty()
    background_color = StringProperty()

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.styler = JetBrainsDark
        self.background_color = self.styler.background_color
        self.raw_text = text

    def on_raw_text(self, _, new):
        # Wrap in BBCode
        bb_text = f"[color={self.styler.styles[Token.Text]}]{new}[/color]"
        self.text = bb_text
