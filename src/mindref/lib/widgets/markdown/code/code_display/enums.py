from __future__ import annotations

from enum import StrEnum, auto


class HandleRole(StrEnum):
    """Which end of a selection a handle drags."""

    start = auto()
    end = auto()
