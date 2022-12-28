from kivy.properties import NumericProperty, ListProperty, Clock
from kivy.uix.effectwidget import AdvancedEffectBase, EffectWidget

effect_string = """
uniform vec2 touch;
uniform float touch_time;
uniform float intensity;
uniform float growth_rate;

vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{
    // color - the normal color of the pixel (texture sampled at tex_coords)
    // texture - the texture containing the widget's normal background
    // tex_coords - the normal texture coordinates used to access the texture
    // coords - the pixel indices of the current pixel
    
    vec2 st = coords.xy / resolution.xy;
    float dist = distance(st, touch);
    
    
    // Calculate the intensity of the lightening effect based on the distance
    // from the touch point.
    
    float radius = touch_time / growth_rate;
    
    // The intensity of the lightening effect is inversely proportional to the distance
    // from the touch point.
    if (dist < radius) {
        float intensity = (radius - dist) / radius;
        float theta = intensity * 0.5;
        color.rgb += sin(theta);
        }
    
    
    
    // Apply the effect to the color.
    
    return color;
}
"""


class TouchRippleEffect(AdvancedEffectBase):
    touch = ListProperty([0.0, 0.0])
    growth_rate = NumericProperty(5.0)
    touch_time = NumericProperty(0.0)
    intensity = NumericProperty(0.9)

    """
    Adds a spreading light effect to the widget. This should have a custom EffectWidget as a parent. One that has a way
    to handle touch events.
    
    Attributes
    ----------
    touch : ListProperty
        The position of the touch event.
    touch_time : NumericProperty
        The time since the touch event (and is still active).
    intensity : NumericProperty
        The intensity of the lightening effect.
    growth_rate : NumericProperty
        The rate at which the lightening effect spreads. Larger values result in a slower spread.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glsl = effect_string
        self.uniforms = {
            "touch": [0.0, 0.0],
            "touch_time": 0.0,
            "intensity": self.intensity,
            "growth_rate": self.growth_rate,
        }

        self.increment_touch_timer = Clock.create_trigger(
            self.increment_touch_time, timeout=1 / 60, interval=True
        )
        self.decrement_touch_timer = Clock.create_trigger(
            self.decrement_touch_time, timeout=1 / 60, interval=True
        )

    def show_effect(self, touch):
        """
        When the parent widget receives a touch event that it wishes to handle, it should call this method.

        Parameters
        ----------
        touch

        """

        if touch:
            self.touch = touch.spos
        self.decrement_touch_timer.cancel()
        self.increment_touch_timer()

    def hide_effect(self):
        """
        When the parent widget no longer has a touch event, it should call this method.
        """

        self.increment_touch_timer.cancel()
        self.decrement_touch_timer()

    def on_touch(self, *args, **kwargs):
        self.uniforms["touch"] = [float(i) for i in self.touch]

    def on_touch_time(self, *args, **kwargs):
        self.uniforms["touch_time"] = float(self.touch_time)

    def on_intensity(self, *args, **kwargs):
        self.uniforms["intensity"] = float(self.intensity)

    def increment_touch_time(self, dt):
        self.touch_time = self.touch_time + dt

    def decrement_touch_time(self, dt):
        touch_time = max(self.touch_time - dt, 0)
        if touch_time <= 0:
            self.touch_time = 0.0
            self.touch = [0.0, 0.0]
            return False
        self.touch_time = touch_time


class TouchRippleWidget(EffectWidget):
    """
    A custom EffectWidget that handles touch events and passes them to the TouchRippleEffect.
    """

    intensity = NumericProperty(0.9)
    growth_rate = NumericProperty(5.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect = TouchRippleEffect()
        self.effects = [self.effect]
        fbind = self.fbind
        fbind("intensity", self.effect.setter("intensity"))
        fbind("growth_rate", self.effect.setter("growth_rate"))

        self.effect.hide_effect()

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        self.effect.show_effect(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        self.effect.hide_effect()

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        self.effect.show_effect(touch)
