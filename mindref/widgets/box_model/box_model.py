from kivy.properties import ColorProperty, NumericProperty, ObjectProperty

from utils import import_kv
from widgets.box_model.margin import MarginBox

import_kv(__file__)


class BoxModel(MarginBox):
    """
    Mimics CSS BoxModel

    Attributes
    ----------
    box_margin: AliasProperty
        Alias for padding
    box_padding: VariableListProperty
        PaddingBox sets padding from this attribute
    border_color:
    border_size:

    Notes
    -----
    Use `add_widget_content` rather than `add_widget`



    See Also
    ---------
    https://developer.mozilla.org/en-US/docs/Web/CSS/Containing_block

    - Margin
    - Padding
    - Content
    """

    border_color = ColorProperty()
    border_size = NumericProperty()
    content_box = ObjectProperty()

    def add_widget_content(self, widget, *args, **kwargs):
        return self.content_box.add_widget(widget, *args, **kwargs)
