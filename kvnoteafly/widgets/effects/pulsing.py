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
             // increase d to balance pulsed vs un-pulsed spread
             float d = 0.8;
             vec2 st = coords.xy/resolution;
             float y = cubicPulse(0.5,max(abs(sin(time)),0.6),st.x);
             vec3 cl = vec3(y);
             return vec4(cl,1.0);
         }
"""


class PulsingEffect(EffectBase):
    def __init__(self, *args, **kwargs):
        super(PulsingEffect, self).__init__(*args, **kwargs)
        self.glsl = effect_pulsing
