from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.utils import import_kv
from mindref.lib.widgets.markdown.base.base import MarkdownLabelBase

import_kv(__file__)


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


class MarkdownThematicBreak(BoxLayout):
    ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
