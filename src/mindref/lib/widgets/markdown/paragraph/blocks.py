from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout

Builder.load_string("""
<MarkdownBlockQuote>:
    cols: 1
    size_hint_y: None
    height: self.minimum_height
    padding: dp(10), dp(10), 0, dp(10)
    canvas:
        Color:
            rgba: (*app.colors['Gray-200'][:3], 0.5)
        Rectangle:
            pos: [self.pos[0], self.pos[1] + dp(5)]
            size: [self.size[0], self.size[1] -dp(10)]
        Color:
            rgba: app.colors['Accent-One']
        Rectangle:
            pos: [self.pos[0], self.pos[1] + dp(5)]
            size: [sp(4), self.height - dp(10)]
""")


class MarkdownBlockQuote(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
