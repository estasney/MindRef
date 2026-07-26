from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout

Builder.load_string("""
<MarkdownList>:
    cols: 1
    size_hint_y: None
    height: self.minimum_height
""")


class MarkdownList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
