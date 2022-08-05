from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)

from utils import import_kv
from widgets.markdown.base.base import MarkdownLabelBase

import_kv(__file__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class MarkdownHeading(MarkdownLabelBase):
    level = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MarkdownBlock(MarkdownLabelBase):
    label = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
