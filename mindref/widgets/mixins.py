from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.widget import Widget


class TrackParentPadding(Widget):
    parent_x_pad = NumericProperty()
    parent_y_pad = NumericProperty()
    parent_padding = ReferenceListProperty(parent_x_pad, parent_y_pad)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def on_parent(self, _, value):

        self.parent_padding = self._get_parent_pad(value)

    def _get_parent_pad(self, parent) -> tuple[int, int]:
        p_pad = parent.padding

        if len(p_pad) == 4:
            # left, top, right, bottom
            return max((p_pad[0], p_pad[2])), max((p_pad[1], p_pad[3]))
        elif len(p_pad) == 2:
            return p_pad
        elif len(p_pad) == 1:
            return p_pad, p_pad
        else:
            return 0, 0
