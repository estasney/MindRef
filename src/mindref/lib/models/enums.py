from enum import Enum, StrEnum
from typing import Literal


class AnimationTiming(StrEnum):
    in_back = "in_back"
    in_bounce = "in_bounce"
    in_circ = "in_circ"
    in_cubic = "in_cubic"
    in_elastic = "in_elastic"
    in_expo = "in_expo"
    in_out_back = "in_out_back"
    in_out_bounce = "in_out_bounce"
    in_out_circ = "in_out_circ"
    in_out_cubic = "in_out_cubic"
    in_out_elastic = "in_out_elastic"
    in_out_expo = "in_out_expo"
    in_out_quad = "in_out_quad"
    in_out_quart = "in_out_quart"
    in_out_quint = "in_out_quint"
    in_out_sine = "in_out_sine"
    in_quad = "in_quad"
    in_quart = "in_quart"
    in_quint = "in_quint"
    in_sine = "in_sine"
    linear = "linear"
    out_back = "out_back"
    out_bounce = "out_bounce"
    out_circ = "out_circ"
    out_cubic = "out_cubic"
    out_elastic = "out_elastic"
    out_expo = "out_expo"
    out_quad = "out_quad"
    out_quart = "out_quart"
    out_quint = "out_quint"
    out_sine = "out_sine"


AnimationTimingLit = Literal[
    "in_back",
    "in_bounce",
    "in_circ",
    "in_cubic",
    "in_elastic",
    "in_expo",
    "in_out_back",
    "in_out_bounce",
    "in_out_circ",
    "in_out_cubic",
    "in_out_elastic",
    "in_out_expo",
    "in_out_quad",
    "in_out_quart",
    "in_out_quint",
    "in_out_sine",
    "in_quad",
    "in_quart",
    "in_quint",
    "in_sine",
    "linear",
    "out_back",
    "out_bounce",
    "out_circ",
    "out_cubic",
    "out_elastic",
    "out_expo",
    "out_quad",
    "out_quart",
    "out_quint",
    "out_sine",
]

TAnimationTiming = AnimationTiming | AnimationTimingLit


class MutationStatus(StrEnum):
    idle = "idle"
    pending = "pending"
    error = "error"
    success = "success"


TMutationStatusLit = Literal["idle", "pending", "error", "success"]

TMutationStatus = MutationStatus | TMutationStatusLit
