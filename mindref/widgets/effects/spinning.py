from kivy.properties import NumericProperty
from kivy.uix.effectwidget import EffectBase

effect_spinning = """
#define PI 3.14159265359
#define SPINRATE {spinRate:f}
 

vec4 effect(vec4 color, sampler2D texture, vec2 text_coords, vec2 coords) {{

             vec2 st = coords.xy/resolution;
             st = st * 2.0 - 1.0;
             st.x *= resolution.x / resolution.y;
             
             float ang = time * SPINRATE;
             float c = cos(ang);
             float s = sin(ang);
             mat2 trans = mat2(c, s, -s, c);
             
             st *= trans;
             
             return vec4(st.x,st.y,st.x*st.y, 1.0);
         }}
"""


class SpinningEffect(EffectBase):
    spin_rate = NumericProperty(defaultvalue=10)

    def __init__(self, *args, **kwargs):
        self.spin_rate = kwargs.pop("spin_rate", 10)
        super(SpinningEffect, self).__init__(*args, **kwargs)
        fl = effect_spinning.format(spinRate=self.spin_rate)
        self.glsl = effect_spinning.format(spinRate=self.spin_rate)
