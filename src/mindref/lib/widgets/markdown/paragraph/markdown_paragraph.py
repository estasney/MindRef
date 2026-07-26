from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from pygments import styles

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import styles mindref.lib.widgets.style
<MarkdownParagraph>:
    cols: 1
    size_hint_y: None

    canvas:
        Color:
            rgb: parse_color(root.background_color)
        Rectangle:
            pos: self.x - 1, self.y - 1
            size: self.width + 2, self.height + 2
        Color:
            rgb: parse_color(root.background_color)
        Rectangle:
            pos: self.pos
            size: self.size
    BaseLabel:
        id: content
        markup: False
        valign: 'top'
        text_size: self.width, None
        text: parent.text_content
""")


class MarkdownParagraph(GridLayout):
    text_content = StringProperty()
    content = ObjectProperty()
    background_color = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.styler = styles.get_style_by_name("paraiso-dark")
        self.background_color = self.styler.background_color
