from kivy import Logger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ColorProperty, StringProperty, partial
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

    def __init__(self, **kwargs):
        self._select_anim = None
        self.canvas_rect_color = None
        self.canvas_rect = None
        super().__init__(**kwargs)
        with self.canvas:
            self.canvas_rect_color = Color(rgba=(0, 0, 0, 0))
            self.canvas_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[0, 0, 0, 0], segments=50
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_args):
        if self.canvas_rect:
            self.canvas_rect.pos = self.pos
            self.canvas_rect.size = self.size

    def on_selected(self, _, is_selected: bool):
        Logger.info(f"NavItem: on_selected called with {is_selected}")
        if not self.canvas_rect:  # We have to reschedule this once canvas is ready
            cb = partial(self.on_selected, is_selected=is_selected)
            Clock.schedule_once(cb, 0.1)
            return

        if is_selected:
            if self._select_anim:
                self._select_anim.stop(self.canvas_rect)
            self.canvas_rect.radius = [self.height / 2] * 4
            self._select_anim = Animation(
                pos=(self.x + dp(12), self.y),
                size=(self.width - dp(24), self.height),
                duration=0.1,
                t="in_quad",
            )
            self._select_anim.start(self.canvas_rect)
            self.canvas_rect_color.rgba = self.bg_color_selected
        else:
            if self._select_anim:
                self._select_anim.stop(self.canvas_rect)
            self._select_anim = Animation(size=(0, 0), duration=0.2, t="in_out_quad")
            self._select_anim.start(self.canvas_rect)
            self.canvas_rect_color.rgba = (0, 0, 0, 0)


class NavItem(ButtonBehavior, BoxLayout, DebugLayout, SelectableAnimation):
    text = StringProperty()
    nav_id = StringProperty()
    selected = BooleanProperty(False)
    bg_color_selected = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
