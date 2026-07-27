"""
Hand-written minimal stub for the compiled `kivy.graphics.fbo` module.

Declares only the class identity and texture accessors; expand with real
signatures (kivy 2.3.1 source: kivy/graphics/fbo.pyx) when app code starts
calling into them.
"""

from kivy.graphics.instructions import RenderContext
from kivy.graphics.texture import Texture

__all__ = ("Fbo",)

class Fbo(RenderContext):
    @property
    def texture(self) -> Texture: ...
    @property
    def size(self) -> tuple[int, int]: ...
    def bind(self) -> None: ...
    def release(self) -> None: ...
