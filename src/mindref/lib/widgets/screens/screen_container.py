from kivy.lang import Builder
from kivy.properties import AliasProperty, ColorProperty, ObjectProperty

from mindref.lib.widgets.screens.interactive import InteractScreen

Builder.load_string("""
<ScreenContainer>:
    layout: layout
    background_color: app.colors['Dark']
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        ScatterLayout:
            canvas.before:
                Color:
                    rgba: root.background_color
                Rectangle:
                    size: self.size
                    pos: self.pos
            id: layout
            height: layout_content.minimum_height
            scale: 1
            do_translation: False, False
            do_scale: True
            do_rotation: False
            BoxLayout:
                id: layout_content
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 0
                spacing: 0
                size_hint: None, None
                width: root.width




""")


class ScreenContainer(InteractScreen):
    """
    Generic Screen that implements a ScatterLayout as its root widget.

    Attributes
    ----------
    layout : ObjectProperty
        BoxLayout that holds the content. Layout is a ScatterLayout that is defined in the kv file.
    content: AliasProperty
        Alias for layout.content
    """

    layout = ObjectProperty()
    background_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_content(self):
        return self.layout.children

    def set_content(self, content):
        self.layout.clear_widgets()
        self.layout.add_widget(content)
        return True

    def on_leave(self, *args):
        self.layout.clear_widgets()
        return super().on_leave(*args)

    content = AliasProperty(getter=get_content, setter=set_content, bind=("layout",))
