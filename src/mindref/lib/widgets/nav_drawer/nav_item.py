from __future__ import annotations

from dataclasses import dataclass
from functools import partial

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from mindref.app_notes import NoteFile
from mindref.lib.models import AnimationTiming
from mindref.lib.utils import required
from mindref.lib.widgets.behavior import DebugBoxLayout

Builder.load_string("""

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
        font_size: sp(app.base_font_size)
        halign: 'center'
        valign: 'middle'

""")


class SelectableAnimation(Widget):
    selected = BooleanProperty(False)
    bg_color_selected = ColorProperty()
    bg_color_unselected = ColorProperty((0, 0, 0, 0))
    canvas_rect_segments = NumericProperty(50)
    canvas_ready_retry_delay = NumericProperty(0.1)
    selected_inset_x = NumericProperty(dp(12))
    animation_select_duration = NumericProperty(0.1)
    animation_select_timing: OptionProperty[AnimationTiming] = OptionProperty(
        AnimationTiming.in_quad, options=tuple(AnimationTiming)
    )
    animation_deselect_duration = NumericProperty(0.2)
    animation_deselect_timing: OptionProperty[AnimationTiming] = OptionProperty(
        AnimationTiming.in_out_quad, options=tuple(AnimationTiming)
    )

    def __init__(self, **kwargs: object):
        self._select_anim = None
        self.canvas_rect_color = None
        self.canvas_rect = None
        super().__init__(**kwargs)
        with self.canvas:
            self.canvas_rect_color = Color(rgba=self.bg_color_unselected)
            self.canvas_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0, 0, 0, 0],
                segments=int(self.canvas_rect_segments),
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_args: object) -> None:
        if self.canvas_rect:
            self.canvas_rect.pos = self.pos
            self.canvas_rect.size = self.size

    def on_selected(self, _instance: object, is_selected: bool) -> None:
        if not self.canvas_rect:  # We have to reschedule this once canvas is ready
            cb = partial(self.on_selected, is_selected=is_selected)
            Clock.schedule_once(cb, self.canvas_ready_retry_delay)
            return

        rect_color = required(self.canvas_rect_color, "canvas_rect_color not set")

        if is_selected:
            if self._select_anim:
                self._select_anim.stop(self.canvas_rect)
            self.canvas_rect.radius = [self.height / 2] * 4
            self._select_anim = Animation(
                pos=(self.x + self.selected_inset_x, self.y),
                size=(self.width - (2 * self.selected_inset_x), self.height),
                duration=self.animation_select_duration,
                t=self.animation_select_timing,
            )
            self._select_anim.start(self.canvas_rect)
            rect_color.rgba = self.bg_color_selected
        else:
            if self._select_anim:
                self._select_anim.stop(self.canvas_rect)
            self._select_anim = Animation(
                size=(0, 0),
                duration=self.animation_deselect_duration,
                t=self.animation_deselect_timing,
            )
            self._select_anim.start(self.canvas_rect)
            rect_color.rgba = self.bg_color_unselected


@dataclass()
class NavItemData:
    display_name: str
    nav_id: str
    selected: bool

    @classmethod
    def from_note_file(cls, data: NoteFile, selected: bool) -> NavItemData:
        return cls(display_name=data.label, nav_id=data.id, selected=selected)


class NavItem(ButtonBehavior, DebugBoxLayout, SelectableAnimation):
    text = StringProperty()
    nav_id = StringProperty()
    selected = BooleanProperty(False)
    bg_color_selected = ColorProperty()

    def __init__(self, text: str, nav_id: str, selected: bool, **kwargs: object):
        super().__init__(**kwargs)
        self.text = text
        self.nav_id = nav_id
        self.selected = selected
