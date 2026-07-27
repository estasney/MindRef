"""
Hand-written minimal stub for the compiled `kivy.graphics.texture` module.

Declares only the class identities and the cheap read-only surface; expand
with real signatures (kivy 2.3.1 source: kivy/graphics/texture.pyx) when app
code starts calling into them.
"""

__all__ = ("Texture", "TextureRegion")

class Texture:
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def size(self) -> tuple[int, int]: ...
    @property
    def id(self) -> int: ...

class TextureRegion(Texture): ...
