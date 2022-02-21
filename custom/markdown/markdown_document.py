import marko

from kivy.properties import (
    AliasProperty,
    Clock,
    DictProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex, get_hex_from_color

from custom.markdown.list.markdown_list import MarkdownList

from custom.markdown.list.markdown_list_item import MarkdownListItem
from custom.markdown.markdown_heading import MarkdownHeading
from utils import import_kv

import_kv(__file__)


class MarkdownDocument(ScrollView):
    text = StringProperty(None)
    base_font_size = NumericProperty(31)

    def _get_bgc(self):
        return get_color_from_hex(self.colors.background)

    def _set_bgc(self, value):
        self.colors.background = get_hex_from_color(value)[1:]

    background_color = AliasProperty(_get_bgc, _set_bgc, bind=("colors",), cache=True)

    colors = DictProperty(
        {
            "background": "37474fff",
            "link": "ce5c00ff",
            "paragraph": "202020ff",
            "title": "204a87ff",
            "bullet": "000000ff",
        }
    )
    underline_color = StringProperty("000000ff")
    content = ObjectProperty(None)

    def __init__(self, content_data: dict, **kwargs):
        super(MarkdownDocument, self).__init__(**kwargs)
        self._parser = marko.Parser()
        self.text = content_data["text"]
        self.current = None
        self.current_params = None

    def on_text(self, instance, value):
        self._load_from_text()

    def render(self):
        self._load_from_text()

    def _get_node_text(self, node):
        if isinstance(node.children, str):
            return node.children
        if len(node.children) > 1:
            raise AttributeError(f"Multiple {len(node.children)}")
        return self._get_node_text(node.children[0])


    def _load_list_node(self, node: "marko.block.List"):
        list_widget = MarkdownList()
        self.content.add_widget(list_widget)
        self.current = list_widget
        for child in node.children:
            self._load_list_item(child, node.start)

    def _load_list_item(self, node: "marko.block.ListItem", level: int):

        list_item = MarkdownListItem(text=self._get_node_text(node), level=level)
        self.current.add_widget(list_item)




    def _load_node(self, node: "marko.block"):
        cls = node.__class__
        if cls is marko.block.Heading:
            label = MarkdownHeading(
                document=self,
                level=node.level,
                content=node.children[0].children,
            )
            self.content.add_widget(label)

        elif cls is marko.block.List:
            self._load_list_node(node)

    def _load_from_text(self, *args):
        self.content.clear_widgets()
        document = self._parser.parse(self.text)
        for child in document.children:
            self._load_node(child)
