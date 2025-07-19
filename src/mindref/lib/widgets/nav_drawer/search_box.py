from kivy.lang import Builder

from mindref.lib.widgets.style import StyledTextInput

Builder.load_string(
    """
#:import StyledTextInput mindref.lib.widgets.style.StyledTextInput
<SearchBox@StyledTextInput>:
    size_hint_x: 1
    size_hint_y: None
    multiline: False
    height: self.minimum_height
    padding: [dp(8), (self.height - self.line_height) / 2, dp(8), 0]
    hint_text: "Search"    
"""
)


class SearchBox(StyledTextInput): ...
