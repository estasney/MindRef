from kivy.lang import Builder
from kivy.properties import AliasProperty, ListProperty, NumericProperty

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
        text_threshold: 170
        valign: root.valign
        halign: root.halign
        height: self.texture_size[1]
        size_hint_y: None
""")


class MarkdownListItem(MarkdownLabelBase):
    level = NumericProperty(1)
    _snippets = ListProperty()

    def get_snippets(self):
        prefix = "  " * self.level
        prefix += f"{chr(8226)} "
        return [
            TextSnippet(text=prefix, highlight_tag=None),
            *(s for s in self._snippets if chr(8226) not in s.text),
        ]

    def set_snippets(self, value):
        self._snippets = value

        return True

    snippets = AliasProperty(
        get_snippets,
        set_snippets,
        bind=("_snippets", "level"),
        cache=True,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
