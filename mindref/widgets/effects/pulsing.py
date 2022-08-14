from kivy.base import EventLoop
from kivy.uix.effectwidget import EffectBase

effect_pulsing = """
//  Function from Iñigo Quiles
//  www.iquilezles.org/www/articles/functions/functions.htm
float cubicPulse( float c, float w, float x ){
    x = abs(x - c);
    if( x>w ) return 0.0;
    x /= w;
    return 1.0 - x*x*(3.0-2.0*x);
}

vec4 effect(vec4 color, sampler2D texture, vec2 text_coords, vec2 coords) {
    float d = 0.8;
    vec2 st = coords.xy/resolution;
    float y = cubicPulse(0.5, max(abs(sin(time)), 0.6), st.x);
    vec4 cl = vec4(y, y, y, 1.0);
    // This is required to avoid Android crashing
    return (texture2D (texture, text_coords) * cl);
}

"""


class PulsingEffect(EffectBase):
    def __init__(self, *args, **kwargs):
        EventLoop.ensure_window()
        super(PulsingEffect, self).__init__(*args, **kwargs)
        self.glsl = effect_pulsing
