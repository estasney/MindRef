from __future__ import annotations

from kivy.lang import Builder
from kivy.properties import AliasProperty, ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from mindref.lib.widgets.markdown.code.code_display.code_display import CodeDisplay
from mindref.lib.widgets.markdown.code.code_display.jetbrains_dark import JetBrainsDark

Builder.load_string("""
#:import parse_color kivy.parser.parse_color
#:import JetBrainsDark mindref.lib.widgets.markdown.code.code_display.jetbrains_dark.JetBrainsDark
#:import SelectThroughScrollView mindref.lib.widgets.select_through_scroll_view.SelectThroughScrollView
<MarkdownCode>:
    cols: 1
    content: content
    size_hint_y: None
    height: content.minimum_height
    canvas:
        Color:
            rgb: parse_color(root.background_color)
        Rectangle:
            pos: self.x - 1, self.y - 1
            size: self.width + 2, self.height + 2
        Color:
            rgb: parse_color(root.background_color)
        Rectangle:
            pos: self.pos
            size: self.size
    SelectThroughScrollView:
        id: scroller
        size_hint_y: None
        height: content.minimum_height
        do_scroll_x: True
        do_scroll_y: False
        effect_cls: "ScrollEffect"
        bar_width: dp(4)
        scroll_type: ["bars", "content"]
        CodeDisplay:
            id: content
            size_hint: None, None
            width: max(scroller.width, self.minimum_width)
            height: self.minimum_height
            text: root.text_content
            style: JetBrainsDark
            lexer_name: root.lexer_name
""")


class MarkdownCode(GridLayout):
    _text_content = StringProperty()
    content: ObjectProperty[CodeDisplay] = ObjectProperty()
    background_color = StringProperty()
    lexer_name = StringProperty()

    def _get_text_content(self) -> str:
        return self._text_content

    def _set_text_content(self, value: str) -> None:
        self._text_content = value.strip()

    text_content: AliasProperty[str] = AliasProperty(
        _get_text_content, _set_text_content, bind=["_text_content"]
    )

    def __init__(self, lexer: str | None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.styler = JetBrainsDark
        self.lexer_name = lexer.strip() if lexer else "markdown"
        self.background_color = self.styler.background_color
