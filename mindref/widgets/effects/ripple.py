from kivy.clock import Clock
from kivy.graphics import RenderContext
from kivy.properties import (
    ListProperty,
    NumericProperty,
    BoundedNumericProperty,
    StringProperty,
)
from kivy.uix.widget import Widget

fs_header = """
$HEADER$
uniform vec2 touch;
uniform float touch_time;
uniform float intensity;
"""

fs_main = """
void main(void) {

            vec4 color = frag_color * texture2D(texture0, tex_coord0);
            float dist = distance(touch, tex_coord0);
            float radius = touch_time;
            if (dist < radius) {
              float pct = (radius - dist) / radius;
              float theta = pct * pct * intensity;
              color.rgb += theta;
            }
            
            gl_FragColor = color;
}
"""


class RippleMixin:
    touch = ListProperty([0.0, 0.0])
    touch_time = NumericProperty(0.0)
    intensity = BoundedNumericProperty(0.9, min=0, max=1)
    growth_rate = NumericProperty(0.2)
    fs = StringProperty()
    size: list[int, int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True,
            use_parent_frag_modelview=True,
        )
        self.has_touch_trigger = Clock.create_trigger(
            self.increment_touch_time, interval=True, timeout=1 / 60
        )
        self.no_touch_trigger = Clock.create_trigger(
            self.decrement_touch_time, interval=True, timeout=1 / 60
        )
        Clock.schedule_interval(self.update_glsl, 1.0 / 60.0)
        Clock.schedule_once(lambda dt: setattr(self, "fs", fs_header + fs_main), 1 / 60)

    def update_glsl(self, _dt):
        """
        Update the GLSL uniforms
        """
        canvas = self.canvas
        canvas["time"] = Clock.get_boottime()
        canvas["resolution"] = [float(x) for x in self.size]
        canvas["touch"] = [float(x) for x in self.touch]
        canvas["touch_time"] = float(self.touch_time)
        canvas["intensity"] = float(self.intensity)
        canvas.ask_update()

    def on_fs(self, _instance, value):
        """
        Update the fragment shader
        """
        shader = self.canvas.shader
        old_value = shader.fs

        shader.fs = value
        if not shader.success:
            shader.fs = old_value

    def increment_touch_time(self, dt):
        """
        Increase the touch_time since the touch event is still active
        We limit the touch_time to 1.0 so that the effect can fill the texture, but we want it to decrement from a maximum of 1.0,
        otherwise the effect will take too long to disappear.
        """
        self.touch_time = min(self.touch_time + dt / self.growth_rate, 1.0)

    def decrement_touch_time(self, dt):
        touch_time = max(self.touch_time - dt, 0)
        if touch_time == 0:
            self.touch_time = 0.0
            self.touch = [0.0, 0.0]
            # Cancel the trigger
            return False
        self.touch_time = touch_time
