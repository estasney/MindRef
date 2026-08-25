"""
Hand-written minimal stub for the compiled `kivy.graphics.texture` module.

Declares only the class identities and the cheap read-only surface; expand
with real signatures (kivy 2.3.1 source: kivy/graphics/texture.pyx) when app
code starts calling into them.
"""

from collections.abc import Callable

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
    @staticmethod
    def create(
        size: tuple[int, int] | None = None,
        colorfmt: str | None = None,
        bufferfmt: str | None = None,
        mipmap: bool = False,
        callback: "Callable[[Texture], None] | None" = None,
        icolorfmt: str | None = None,
    ) -> "Texture": ...
    def blit_buffer(
        self,
        pbuffer: bytes | bytearray | memoryview,
        size: tuple[int, int] | None = None,
        colorfmt: str | None = None,
        pos: tuple[int, int] | None = None,
        bufferfmt: str | None = None,
        mipmap_level: int = 0,
        mipmap_generation: bool = True,
        rowlength: int = 0,
    ) -> None: ...

class TextureRegion(Texture): ...
