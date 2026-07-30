from kivy.lang import Builder
from kivy.properties import NumericProperty

from mindref.lib.widgets.behavior.inline_behavior import TextSnippet
from mindref.lib.widgets.markdown.base.base import MarkdownLabelBase

Builder.load_string("""
#:import styles mindref.lib.widgets.style
#:import LabelHighlightInline mindref.lib.widgets.behavior

<MarkdownListItem>:
    label: label
    cols: 1
    size_hint_y: None
    height: label.texture_size[1] + dp(20)
    x: 0
    LabelHighlightInline:
        id: label
        snippets: root.snippets
        bg_color: app.colors['Primary']
        highlight_color: app.colors['Codespan']
        valign: root.valign
        halign: root.halign
        height: self.texture_size[1]
        size_hint_y: None
""")


class MarkdownListItem(MarkdownLabelBase):
    level = NumericProperty(1)

    def get_snippets(self) -> list[TextSnippet]:
        return self.snippets

    def set_snippets(self, value: list[TextSnippet]) -> None:
        prefix = "  " * int(self.level) + f"{chr(8226)} "
        self.snippets = [
            TextSnippet(text=prefix, highlight_tag=None),
            *(s for s in value if chr(8226) not in s.text),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
