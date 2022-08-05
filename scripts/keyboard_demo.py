from pathlib import Path

import mistune
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.parser import parse_color
from kivy.properties import DictProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from mindref.domain.parser.kbd_plugin import plugin_kbd
from mindref.widgets.behavior.inline_behavior import TextSnippet, LabelHighlightInline

doc = """
# KeyboardDemo

<kbd>Shift</kbd> + <kbd>A</kbd>

<kbd>Shift</kbd> + <kbd>Space</kbd>
"""

md = mistune.create_markdown(
    renderer=mistune.AstRenderer(), plugins=[plugin_kbd, "table"]
)


class KeyContainer(BoxLayout):
    snippets = ListProperty()
    level = NumericProperty(defaultvalue=1)


class DemoContainer(ScrollView):
    content: ObjectProperty()


Factory.register("KeyContainer", cls=KeyContainer)
Factory.register("DemoContainer", cls=DemoContainer)

Builder.load_string(
    """
<DemoContainer>:
    content: content
    do_scroll_x: False
    canvas.before:
        Color:
            rgba: app.colors['Primary']
        Rectangle:
            pos: self.pos
            size: self.size
    Scatter:
        id: scatter
        size_hint_y: None
        height: content.minimum_height
        width: root.width
        scale: 1
        do_translation: False, False
        do_scale: False
        do_rotation: False
        GridLayout:
            size_hint_y: None
            id: content
            cols: 1
            height: self.minimum_height
            width: root.width
            padding: dp(10)
            
<KeyContainer>:
    pos_hint: {'center': 0}
    orientation: 'horizontal'
    size_hint_y: None
    height: self.minimum_height
    size_hint_x: 1
    label: label
    LabelHighlightInline:
        
        id: label
        snippets: root.snippets
        bg_color: app.colors['Primary']
        highlight_color: app.colors['Codespan']
        valign: 'center'
        halign: 'left'
        height: self.texture_size[1] + dp(20)
        size_hint_y: None
        font_size: app.base_font_size
        padding: (dp(0), 0)

""",
    rulesonly=True,
)


class DemoApp(App):
    base_font_size: NumericProperty()
    fonts = DictProperty({"mono": "RobotoMono", "default": "Roboto"})
    colors = DictProperty(
        {
            "White": (1, 1, 1),
            "Gray-100": parse_color("#f3f3f3"),
            "Gray-200": parse_color("#dddedf"),
            "Gray-300": parse_color("#c7c8ca"),
            "Gray-400": parse_color("#9a9da1"),  # White text
            "Gray-500": parse_color("#6d7278"),
            "Codespan": parse_color("#00000026"),
            "Keyboard": parse_color("#d9d9d9"),
            "KeyboardShadow": parse_color("#656565"),
            "Primary": parse_color("#37464f"),
            "Dark": parse_color("#101f27"),
            "Accent-One": parse_color("#388fe5"),
            "Accent-Two": parse_color("#56e39f"),
            "Warn": parse_color("#fa1919"),
        }
    )

    def __init__(self):
        super(DemoApp, self).__init__()
        self.base_font_size = 16

    def build(self):
        root = DemoContainer()
        md_doc = md.parse(doc)
        for item in md_doc:
            if item["type"] == "paragraph":
                demo_widget = KeyContainer()
                for child in item["children"]:
                    demo_widget.snippets.append(
                        TextSnippet(
                            text=child["text"],
                            highlight_tag="kbd" if child["type"] == "kbd" else None,
                        )
                    )
                root.content.add_widget(demo_widget)

        return root


if __name__ == "__main__":
    LabelBase.register(
        name="RobotoMono",
        fn_regular=str(
            Path(__file__).parent.parent
            / "mindref"
            / "assets"
            / "RobotoMono-Regular.ttf"
        ),
    )
    DemoApp().run()
