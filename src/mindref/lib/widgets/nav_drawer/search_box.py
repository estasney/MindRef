from kivy.lang import Builder
from kivy.uix.textinput import TextInput

Builder.load_string(
    """
<SearchBox@TextInput>
    size_hint_x: 1
    size_hint_y: None
    multiline: False
    height: self.minimum_height
    background_normal: ''
    background_active: ''
    background_color: 0, 0, 0, 0
    cursor_color: app.colors['Gray-600']
    foreground_color: 1, 1, 1, 1
    padding: [dp(8), (self.height - self.line_height) / 2, dp(8), 0]
    hint_text: "Search"
    
    canvas.after:
        Color:
            rgba: [*app.colors['Gray-800'][:3], 0.1]
        RoundedRectangle:
            pos: [self.x, self.y - dp(8)]
            size: [self.width, self.height+(2*dp(8))]
            radius: [dp(4), dp(4), dp(4), dp(4)]
        Color:
            rgba: [*app.colors['Gray-800'][:3], 0.2] if not self.focus else [*app.colors['Gray-800'][:3], 0.4]
        Line:
            points: [self.x, self.y - dp(8), self.x + self.width, self.y - dp(8)]
            width: dp(1)
    
"""
)


class SearchBox(TextInput): ...
