from kivy.properties import ListProperty, NumericProperty
from kivy.uix.effectwidget import EffectBase

effect_linear_gradient = """

float cubicPulse(float c, float w, float x) {{
    x = abs(x - c);
    if (x > w) return 0.0;
    x /= w;
    return 1.0 - x * x * (3.0 - 2.0 * x);
}}


vec4 effect(vec4 color, sampler2D texture, vec2 tex, vec2 px)
{{
    vec2 st = px / resolution;          // 0-1 space

    // Head of the “bar” moves left→right and wraps
    float centre = mod(time * {speed:.3f}, 1.0 + {bar_w:.3f}) - {bar_w:.3f} * 0.5;
    float alpha  = cubicPulse(centre, {bar_w:.3f} * 0.5, st.x);

    // Linear gradient through the bar
    float t = clamp((st.x - (centre - {bar_w:.3f} * 0.5)) / {bar_w:.3f}, 0.0, 1.0);
    vec3  grad = mix({grad_start}, {grad_end}, t);

    vec4 bar  = vec4(grad * alpha, alpha);
    vec4 base = texture2D(texture, tex);  // underlying track

    return mix(base, bar, bar.a);          // overlay bar on track
}}
"""


class LinearProgressEffect(EffectBase):
    """Animated linear gradient"""

    grad_start = ListProperty([0.06, 0.50, 0.98])
    grad_end = ListProperty([0.38, 0.80, 1.00])
    speed = NumericProperty(3.5)
    bar_width = NumericProperty(3.0)

    def __init__(self, **kwargs: object):
        super().__init__(**kwargs)
        self.do_glsl()

    def do_glsl(self):
        """
        Generate the GLSL shader code for the effect.
        """
        vec_3_grad_start = "vec3({:.3f}, {:.3f}, {:.3f})".format(*self.grad_start)
        vec_3_grad_end = "vec3({:.3f}, {:.3f}, {:.3f})".format(*self.grad_end)
        self.glsl = effect_linear_gradient.format(
            speed=self.speed,
            bar_w=self.bar_width,
            grad_start=vec_3_grad_start,
            grad_end=vec_3_grad_end,
        )
