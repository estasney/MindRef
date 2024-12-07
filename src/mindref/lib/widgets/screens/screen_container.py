from kivy.properties import AliasProperty, ColorProperty, ObjectProperty

from mindref.lib.utils import import_kv
from mindref.lib.widgets.screens import InteractScreen

import_kv(__file__)


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
