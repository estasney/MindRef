from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from math import radians, tan

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import (
    Color,
    Rectangle,
    RoundedRectangle,
    StencilPop,
    StencilPush,
    StencilUnUse,
    StencilUse,
)
from kivy.graphics.texture import Texture
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


def build_shimmer_texture(width: int = 256) -> Texture:
    """Horizontal white band: alpha ramps up to a peak at 50%, gone by 80%."""
    texture = Texture.create(size=(width, 1), colorfmt="rgba")
    buffer = bytearray()
    for i in range(width):
        t = i / (width - 1)
        if t <= 0.5:
            rise = t / 0.5
        elif t <= 0.8:
            rise = (0.8 - t) / 0.3
        else:
            rise = 0.0
        buffer += bytes((255, 255, 255, int(255 * rise)))
    texture.blit_buffer(bytes(buffer), colorfmt="rgba", bufferfmt="ubyte")
    return texture


class SelectableAnimation(Widget):
    selected = BooleanProperty(False)
    shimmering = BooleanProperty(False)
    shimmer_alpha = NumericProperty(0.5)
    shimmer_band_fraction = NumericProperty(0.26)
    shimmer_duration = NumericProperty(1.0)
    shimmer_slant_degrees = NumericProperty(10.0)
    shimmer_travel_overshoot = NumericProperty(1.5)
    shimmer_progress = NumericProperty(0.0)
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
        self.shimmer_anim: Animation | None = None
        super().__init__(**kwargs)
        with self.canvas:
            self.canvas_rect_color = Color(rgba=self.bg_color_unselected)
            self.canvas_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0, 0, 0, 0],
                segments=int(self.canvas_rect_segments),
            )
            StencilPush()
            self.shimmer_stencil = RoundedRectangle(
                pos=self.pos, size=(0, 0), segments=int(self.canvas_rect_segments)
            )
            StencilUse()
            self.shimmer_color = Color(rgba=(1, 1, 1, 0))
            self.shimmer_rect = Rectangle(
                pos=self.pos, size=(0, 0), texture=build_shimmer_texture()
            )
            StencilUnUse()
            self.shimmer_stencil_undo = RoundedRectangle(
                pos=self.pos, size=(0, 0), segments=int(self.canvas_rect_segments)
            )
            StencilPop()
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_args: object) -> None:
        if self.canvas_rect:
            self.canvas_rect.pos = self.pos
            self.canvas_rect.size = self.size
        if self.shimmering:
            self.place_shimmer()

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

    def shimmer_frame(self) -> tuple[float, float, float, float]:
        """The inset rounded-rect region the selection highlight occupies."""
        inset = self.selected_inset_x
        return self.x + inset, self.y, self.width - (2 * inset), self.height

    def place_shimmer(self) -> None:
        x, y, width, height = self.shimmer_frame()
        for stencil in (self.shimmer_stencil, self.shimmer_stencil_undo):
            stencil.pos = (x, y)
            stencil.size = (width, height)
            stencil.radius = [height / 2] * 4
        band_width = width * self.shimmer_band_fraction
        travel = (width + band_width) * self.shimmer_travel_overshoot
        shear = (height * tan(radians(self.shimmer_slant_degrees))) / band_width
        self.shimmer_rect.size = (band_width, height)
        self.shimmer_rect.tex_coords = (0, 0, 1, 0, 1 - shear, 1, -shear, 1)
        self.shimmer_rect.pos = (
            x - band_width + (self.shimmer_progress * travel),
            y,
        )

    def on_shimmer_progress(self, _instance: object, _progress: float) -> None:
        if self.shimmering:
            self.place_shimmer()

    def on_shimmering(self, _instance: object, shimmering: bool) -> None:
        if self.shimmer_anim is not None:
            self.shimmer_anim.cancel(self)
            self.shimmer_anim = None
        if shimmering:
            self.shimmer_progress = 0
            self.shimmer_color.rgba = (1, 1, 1, self.shimmer_alpha)
            self.place_shimmer()
            sweep = Animation(shimmer_progress=1.0, duration=self.shimmer_duration)
            sweep += Animation(shimmer_progress=0.0, duration=0)
            sweep.repeat = True
            self.shimmer_anim = sweep
            sweep.start(self)
        else:
            self.shimmer_color.rgba = (1, 1, 1, 0)


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
