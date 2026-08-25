"""
Hand-written stub. `kivy.graphics.vertex_instructions` is a compiled Cython
module, so pyright's stub generator had no source to read. Signatures follow the
kivy 2.3.1 sources in `.claude/kivy`; `Line` and `SmoothLine` live in the
included `vertex_instructions_line.pxi`.

Geometry properties are `Sequence[float]` on both sides: the getters return
lists or tuples, the setters take any sequence of the right length. `Line`
additionally accepts a sequence of point pairs for `points`; the stub describes
only the flat form.
"""

from collections.abc import Sequence
from typing import Any, Literal

from kivy.graphics.instructions import VertexInstruction

__all__ = (
    "Triangle",
    "Quad",
    "Rectangle",
    "RoundedRectangle",
    "BorderImage",
    "Ellipse",
    "Line",
    "Point",
    "Mesh",
    "GraphicException",
    "Bezier",
    "SmoothLine",
)

type TMeshMode = Literal[
    "points",
    "line_strip",
    "line_loop",
    "lines",
    "triangles",
    "triangle_strip",
    "triangle_fan",
]
type TLineCap = Literal["none", "square", "round"]
type TLineJoint = Literal["none", "miter", "bevel", "round"]
type TLineCloseMode = Literal["straight-line", "center-connected"]
type TBorderAutoScale = Literal[
    "off",
    "both",
    "x_only",
    "y_only",
    "y_full_x_lower",
    "x_full_y_lower",
    "both_lower",
]

class GraphicException(Exception): ...

class Bezier(VertexInstruction):
    def __init__(
        self,
        *,
        points: Sequence[float] = ...,
        segments: int = ...,
        loop: bool = ...,
        dash_length: int = ...,
        dash_offset: int = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def points(self) -> Sequence[float]: ...
    @points.setter
    def points(self, value: Sequence[float]) -> None: ...
    @property
    def segments(self) -> int: ...
    @segments.setter
    def segments(self, value: int) -> None: ...
    @property
    def dash_length(self) -> int: ...
    @dash_length.setter
    def dash_length(self, value: int) -> None: ...
    @property
    def dash_offset(self) -> int: ...
    @dash_offset.setter
    def dash_offset(self, value: int) -> None: ...

class Mesh(VertexInstruction):
    def __init__(
        self,
        *,
        vertices: Sequence[float] = ...,
        indices: Sequence[int] = ...,
        mode: TMeshMode = ...,
        fmt: Sequence[tuple[str, int, str]] = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def vertices(self) -> Sequence[float]: ...
    @vertices.setter
    def vertices(self, value: Sequence[float]) -> None: ...
    @property
    def indices(self) -> Sequence[int]: ...
    @indices.setter
    def indices(self, value: Sequence[int]) -> None: ...
    @property
    def mode(self) -> TMeshMode: ...
    @mode.setter
    def mode(self, value: TMeshMode) -> None: ...

class Point(VertexInstruction):
    def __init__(
        self,
        *,
        points: Sequence[float] = ...,
        pointsize: float = ...,
        **kwargs: Any,
    ) -> None: ...
    def add_point(self, x: float, y: float) -> None: ...
    @property
    def points(self) -> Sequence[float]: ...
    @points.setter
    def points(self, value: Sequence[float]) -> None: ...
    @property
    def pointsize(self) -> float: ...
    @pointsize.setter
    def pointsize(self, value: float) -> None: ...

class Triangle(VertexInstruction):
    def __init__(self, *, points: Sequence[float] = ..., **kwargs: Any) -> None: ...
    @property
    def points(self) -> Sequence[float]: ...
    @points.setter
    def points(self, value: Sequence[float]) -> None: ...

class Quad(VertexInstruction):
    def __init__(self, *, points: Sequence[float] = ..., **kwargs: Any) -> None: ...
    @property
    def points(self) -> Sequence[float]: ...
    @points.setter
    def points(self, value: Sequence[float]) -> None: ...

class Rectangle(VertexInstruction):
    def __init__(
        self,
        *,
        pos: Sequence[float] = ...,
        size: Sequence[float] = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def pos(self) -> Sequence[float]: ...
    @pos.setter
    def pos(self, value: Sequence[float]) -> None: ...
    @property
    def size(self) -> Sequence[float]: ...
    @size.setter
    def size(self, value: Sequence[float]) -> None: ...
    @property
    def points(self) -> Sequence[float]: ...

class BorderImage(Rectangle):
    def __init__(
        self,
        *,
        border: Sequence[float] = ...,
        auto_scale: TBorderAutoScale = ...,
        display_border: Sequence[float] = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def border(self) -> Sequence[float]: ...
    @border.setter
    def border(self, value: Sequence[float]) -> None: ...
    @property
    def auto_scale(self) -> TBorderAutoScale: ...
    @auto_scale.setter
    def auto_scale(self, value: TBorderAutoScale) -> None: ...
    @property
    def display_border(self) -> Sequence[float]: ...
    @display_border.setter
    def display_border(self, value: Sequence[float]) -> None: ...

class Ellipse(Rectangle):
    def __init__(
        self,
        *,
        segments: int = ...,
        angle_start: float = ...,
        angle_end: float = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def segments(self) -> int: ...
    @segments.setter
    def segments(self, value: int) -> None: ...
    @property
    def angle_start(self) -> float: ...
    @angle_start.setter
    def angle_start(self, value: float) -> None: ...
    @property
    def angle_end(self) -> float: ...
    @angle_end.setter
    def angle_end(self, value: float) -> None: ...

class RoundedRectangle(Rectangle):
    def __init__(
        self,
        *,
        segments: int | Sequence[int] = ...,
        radius: Sequence[float] | Sequence[Sequence[float]] = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def segments(self) -> Sequence[int]: ...
    @segments.setter
    def segments(self, value: Sequence[int]) -> None: ...
    @property
    def radius(self) -> Sequence[Sequence[float]]: ...
    @radius.setter
    def radius(self, value: Sequence[float] | Sequence[Sequence[float]]) -> None: ...

class Line(VertexInstruction):
    def __init__(
        self,
        *,
        points: Sequence[float] = ...,
        dashes: Sequence[int] = ...,
        dash_length: int = ...,
        dash_offset: int = ...,
        width: float = ...,
        joint: TLineJoint = ...,
        cap: TLineCap = ...,
        cap_precision: int = ...,
        joint_precision: int = ...,
        bezier_precision: int = ...,
        close: bool = ...,
        close_mode: TLineCloseMode = ...,
        force_custom_drawing_method: bool = ...,
        ellipse: Sequence[float] = ...,
        circle: Sequence[float] = ...,
        rectangle: Sequence[float] = ...,
        rounded_rectangle: Sequence[float] = ...,
        bezier: Sequence[float] = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def points(self) -> Sequence[float]: ...
    @points.setter
    def points(self, value: Sequence[float]) -> None: ...
    @property
    def dashes(self) -> Sequence[int]: ...
    @dashes.setter
    def dashes(self, value: Sequence[int]) -> None: ...
    @property
    def dash_length(self) -> int: ...
    @dash_length.setter
    def dash_length(self, value: int) -> None: ...
    @property
    def dash_offset(self) -> int: ...
    @dash_offset.setter
    def dash_offset(self, value: int) -> None: ...
    @property
    def width(self) -> float: ...
    @width.setter
    def width(self, value: float) -> None: ...
    @property
    def cap(self) -> TLineCap: ...
    @cap.setter
    def cap(self, value: TLineCap) -> None: ...
    @property
    def joint(self) -> TLineJoint: ...
    @joint.setter
    def joint(self, value: TLineJoint) -> None: ...
    @property
    def cap_precision(self) -> int: ...
    @cap_precision.setter
    def cap_precision(self, value: int) -> None: ...
    @property
    def joint_precision(self) -> int: ...
    @joint_precision.setter
    def joint_precision(self, value: int) -> None: ...
    @property
    def close(self) -> int: ...
    @close.setter
    def close(self, value: bool | int) -> None: ...
    @property
    def close_mode(self) -> TLineCloseMode: ...
    @close_mode.setter
    def close_mode(self, value: TLineCloseMode) -> None: ...
    @property
    def force_custom_drawing_method(self) -> int: ...
    @force_custom_drawing_method.setter
    def force_custom_drawing_method(self, value: bool | int) -> None: ...
    @property
    def bezier_precision(self) -> int: ...
    @bezier_precision.setter
    def bezier_precision(self, value: int) -> None: ...
    @property
    def ellipse(self) -> Sequence[float]: ...
    @ellipse.setter
    def ellipse(self, value: Sequence[float]) -> None: ...
    @property
    def circle(self) -> Sequence[float]: ...
    @circle.setter
    def circle(self, value: Sequence[float]) -> None: ...
    @property
    def rectangle(self) -> Sequence[float]: ...
    @rectangle.setter
    def rectangle(self, value: Sequence[float]) -> None: ...
    @property
    def rounded_rectangle(self) -> Sequence[float]: ...
    @rounded_rectangle.setter
    def rounded_rectangle(self, value: Sequence[float]) -> None: ...
    @property
    def bezier(self) -> Sequence[float]: ...
    @bezier.setter
    def bezier(self, value: Sequence[float]) -> None: ...

class SmoothLine(Line):
    def premultiplied_texture(self) -> Any: ...
    @property
    def overdraw_width(self) -> float: ...
    @overdraw_width.setter
    def overdraw_width(self, value: float) -> None: ...

class SmoothRectangle(Rectangle):
    default_texture: Any
    @property
    def antialiasing_line_points(self) -> Sequence[float]: ...

class SmoothRoundedRectangle(RoundedRectangle):
    default_texture: Any
    @property
    def antialiasing_line_points(self) -> Sequence[float]: ...

class SmoothEllipse(Ellipse):
    default_texture: Any
    @property
    def antialiasing_line_points(self) -> Sequence[float]: ...

class SmoothQuad(Quad):
    default_texture: Any
    @property
    def antialiasing_line_points(self) -> Sequence[float]: ...

class SmoothTriangle(Triangle):
    default_texture: Any
    @property
    def antialiasing_line_points(self) -> Sequence[float]: ...
