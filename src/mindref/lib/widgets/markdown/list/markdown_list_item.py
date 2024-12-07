from kivy.properties import AliasProperty, ListProperty, NumericProperty

from mindref.lib.utils import import_kv
from mindref.lib.widgets.behavior.inline_behavior import TextSnippet
from mindref.lib.widgets.markdown.base.base import MarkdownLabelBase

import_kv(__file__)


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
        super(MarkdownListItem, self).__init__(**kwargs)
