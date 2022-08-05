from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv
from widgets.markdown.markdown_interceptor import (
    InterceptingInlineWidgetMixin,
)

import_kv(__file__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class MarkdownHeading(BoxLayout, InterceptingInlineWidgetMixin):
    label = ObjectProperty()
    level = NumericProperty()
    snippets = ListProperty()
    open_bbcode_tag = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MarkdownBlock(BoxLayout, InterceptingInlineWidgetMixin):
    label = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
