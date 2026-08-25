"""
Hand-written stub. `kivy.graphics.stencil_instructions` is a compiled Cython
module. Signatures follow the kivy 2.3.1 sources in `.claude/kivy`.
"""

from kivy.graphics.instructions import Instruction

__all__ = ("StencilPush", "StencilPop", "StencilUse", "StencilUnUse")

class StencilPush(Instruction):
    def __init__(self, *, clear_stencil: bool = True, **kwargs: object) -> None: ...

class StencilPop(Instruction): ...

class StencilUse(Instruction):
    def __init__(self, *, op: str = ..., **kwargs: object) -> None: ...

class StencilUnUse(Instruction): ...
