"""Hand-written stub for `kivy.uix.effectwidget` (kivy 2.3.1).

Widget-facing members carry their property descriptor types so instance
access resolves to the value type. Only the shader-string module constants
are declared loosely; they are internal templates.
"""

from kivy.event import EventDispatcher
from kivy.graphics import Fbo
from kivy.graphics.texture import Texture
from kivy.properties import (
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.relativelayout import RelativeLayout

__all__ = (
    "EffectWidget",
    "EffectBase",
    "AdvancedEffectBase",
    "MonochromeEffect",
    "InvertEffect",
    "ChannelMixEffect",
    "ScanlinesEffect",
    "PixelateEffect",
    "HorizontalBlurEffect",
    "VerticalBlurEffect",
    "FXAAEffect",
)

shader_header: str
shader_uniforms: str
shader_footer_trivial: str
shader_footer_effect: str
effect_trivial: str
effect_monochrome: str
effect_invert: str
effect_mix: str
effect_blur_h: str
effect_blur_v: str
effect_postprocessing: str
effect_pixelate: str
effect_fxaa: str

class EffectBase(EventDispatcher):
    glsl: StringProperty[str]
    source: StringProperty[str]
    fbo: ObjectProperty[EffectFbo | None]
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def set_fbo_shader(self, *args: object) -> None: ...

class AdvancedEffectBase(EffectBase):
    uniforms: DictProperty[str, float | list[float]]
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def set_fbo_shader(self, *args: object) -> None: ...

class MonochromeEffect(EffectBase):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

class InvertEffect(EffectBase):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

class ScanlinesEffect(EffectBase):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

class ChannelMixEffect(EffectBase):
    order: ListProperty[int]
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def on_order(self, *args: object) -> None: ...
    def do_glsl(self) -> None: ...

class PixelateEffect(EffectBase):
    pixel_size: NumericProperty
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def on_pixel_size(self, *args: object) -> None: ...
    def do_glsl(self) -> None: ...

class HorizontalBlurEffect(EffectBase):
    size: NumericProperty
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def on_size(self, *args: object) -> None: ...
    def do_glsl(self) -> None: ...

class VerticalBlurEffect(EffectBase):
    size: NumericProperty
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def on_size(self, *args: object) -> None: ...
    def do_glsl(self) -> None: ...

class FXAAEffect(EffectBase):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

class EffectFbo(Fbo):
    texture_rectangle: object
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def set_fs(self, value: str) -> None: ...

class EffectWidget(RelativeLayout):
    background_color: ListProperty[float]
    texture: ObjectProperty[Texture | None]
    effects: ListProperty[EffectBase]
    fbo_list: ListProperty[EffectFbo]
    def __init__(self, **kwargs: object) -> None: ...
    def refresh_fbo_setup(self, *args: object) -> None: ...
    def add_widget(self, *args: object, **kwargs: object) -> None: ...
    def remove_widget(self, *args: object, **kwargs: object) -> None: ...
    def clear_widgets(self, *args: object, **kwargs: object) -> None: ...
