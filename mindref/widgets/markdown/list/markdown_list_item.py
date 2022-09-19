from kivy.properties import NumericProperty

from utils import import_kv
from widgets.behavior.inline_behavior import TextSnippet
from widgets.markdown.base.base import MarkdownLabelBase

import_kv(__file__)


class MarkdownListItem(MarkdownLabelBase):

    level = NumericProperty(1)

    def __init__(self, **kwargs):
        super(MarkdownListItem, self).__init__(**kwargs)

    def handle_intercept_exit(self):
        # Include Bullet
        prefix = "  " * self.level
        prefix += f"{chr(8226)} "
        snippets = [TextSnippet(text=prefix, highlight_tag=None), *self.snippets]
        self.snippets = snippets
