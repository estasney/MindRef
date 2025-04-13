from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ColorProperty, Logger, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from mindref.lib.widgets.behavior import DebugLayout

Builder.load_string(
    """
#:import Label kivy.uix.label.Label
<NavItem>:
    debug_layout: False
    text: ''
    size_hint_y: None
    height: self.minimum_height
    bg_color_selected: [1,1,1, 0.2]
    Label:
        text: root.text
        text_size: root.width, None # Limit text to the width of the button, but allow it to grow vertically
        size: self.texture_size
        font_size: sp(16)
        halign: 'center'
        valign: 'middle'
"""
)


class SelectableAnimation(Widget):
    selected = BooleanProperty(False)
    bg_color_selected = ColorProperty()
    canvas_rect: RoundedRectangle
    canvas_rect_color: Color
    _select_anim: Animation | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._select_anim = None
        with self.canvas:
            self.canvas_rect_color = Color(rgba=(0, 0, 0, 0))
            self.canvas_rect = RoundedRectangle(
                pos=self.center, size=self.size, radius=[(0, 0, 0, 0)]
            )
        Clock.schedule_once(self._bind_canvas, 0)

    def _bind_canvas(self, _dt):
        self.bind(pos=self._update_canvas)

    def _update_canvas(self, *_args):
        self.canvas_rect.pos = self.center

    def on_selected(self, _, is_selected: bool):
        if is_selected:
            if self._select_anim:
                self._select_anim.stop(self.canvas_rect)
            self.canvas_rect.radius = [self.height / 2, self.height / 2]
            self._select_anim = Animation(
                pos=self.pos, size=(self.width, self.height), duration=0.1, t="in_quad"
            )
            self._select_anim.start(self.canvas_rect)

            self.canvas_rect_color.rgba = self.bg_color_selected
        else:
            if self._select_anim:
                self._select_anim.stop(self.canvas_rect)
            self._select_anim = Animation(size=(0, 0), duration=0.2, t="in_out_quad")
            self.canvas_rect_color.rgba = (0, 0, 0, 0)
            self._select_anim.start(self.canvas_rect)


class NavItem(ButtonBehavior, BoxLayout, DebugLayout, SelectableAnimation):
    """ """

    text = StringProperty()
    nav_id = StringProperty()
    selected = BooleanProperty(False)
    bg_color_selected = ColorProperty()
    _select_anim: Animation | None
    _canvas_rect: RoundedRectangle | None
    _canvas_rect_color: Color | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
