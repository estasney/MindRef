from kivy.base import EventLoop
from kivy.properties import BoundedNumericProperty, NumericProperty
from kivy.uix.effectwidget import EffectBase

# cubicPulse Function from Iñigo Quiles
# www.iquilezles.org/www/articles/functions/functions.htm

effect_vars = """
const float PULSE_WIDTH = {pulse_width:f};
const float PULSE_PERIOD = {pulse_period:f};
const float MIN_COLOR = {min_color:f}; 
"""

effect_pulsing = """
float cubicPulse( float c, float w, float x ) {
    x = abs(x - c);
    if( x>w ) return 0.0;
    x /= w;
    return 1.0 - x*x*(3.0-2.0*x);
}

vec4 effect(vec4 color, sampler2D texture, vec2 text_coords, vec2 coords) {
    vec2 st = coords.xy/resolution; 
    float hlPulse = cubicPulse(tan((time * PULSE_PERIOD)), PULSE_WIDTH, st.x);
    hlPulse += MIN_COLOR;
    vec4 cl = vec4(color.r*(hlPulse), color.g*(hlPulse), color.b*(hlPulse), 1.0);
    // This is required to avoid Android crashing
    return (texture2D (texture, text_coords) * cl);
}
"""


class PulsingEffect(EffectBase):
    pulse_width = BoundedNumericProperty(defaultvalue=0.35, min=1e-1)
    pulse_period = NumericProperty(defaultvalue=0.2)
    min_color = NumericProperty(defaultvalue=0.9)

    """
    Attributes
    ----------
    pulse_width: NumericProperty
        Portion of the texture that is highlighted at any time. Larger values give wider 'beams'
    pulse_period: NumericProperty
        Values closer to zero decrease the speed that the highlight effect passes over. 
        By default beam moves left to right. Pass a negative value to reverse direction.
    min_color: NumericProperty
        Darken the base color by at most this much
        
    
    """

    def __init__(self, *args, **kwargs):
        EventLoop.ensure_window()
        super(PulsingEffect, self).__init__(*args, **kwargs)
        self.bind(
            pulse_width=self.build_shader,
            pulse_period=self.build_shader,
            min_color=self.build_shader,
        )
        self.build_shader()

    def build_shader(self):
        fs_vars = effect_vars.format(
            pulse_width=self.pulse_width,
            pulse_period=self.pulse_period,
            min_color=self.min_color,
        )
        self.glsl = fs_vars + effect_pulsing
