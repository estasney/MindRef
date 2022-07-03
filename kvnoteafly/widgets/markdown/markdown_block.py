from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv
from widgets.markdown.markdown_interceptor import (
    InterceptingInlineWidgetMixin,
    InterceptingWidgetMixin,
)

import_kv(__file__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class MarkdownHeading(BoxLayout, InterceptingWidgetMixin):
    label = ObjectProperty()
    level = NumericProperty()
    is_codespan = BooleanProperty()
    raw_text = StringProperty()
    text = StringProperty()
    open_bbcode_tag = StringProperty()

    def __init__(self, text: str = "", is_codespan: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.is_codespan = is_codespan
        self.raw_text = text
        self.open_bbcode_tag = ""

    def on_raw_text(self, instance, value):
        self.label.raw_text = value


class MarkdownBlock(BoxLayout, InterceptingInlineWidgetMixin):
    label = ObjectProperty()
    open_bbcode_tag = StringProperty()
    snippets = ListProperty()

    def __init__(self, text: str = "", is_codespan: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.is_codespan = is_codespan
        self.raw_text = text
        self.open_bbcode_tag = ""
