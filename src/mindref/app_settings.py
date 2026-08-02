from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kivy.event import EventDispatcher
from kivy.properties import (
    ConfigParserProperty,
)

if TYPE_CHECKING:
    SubscriptableConfigParserProperty = ConfigParserProperty
else:
    # Compiled kivy property classes lack __class_getitem__, so a parameterized
    # base class is a runtime TypeError; this shim absorbs the subscript.
    class SubscriptableConfigParserProperty(ConfigParserProperty):
        def __class_getitem__(cls, item):
            return cls


def _to_path(value: str | Path | None) -> Path | None:
    match value:
        case "None" | "null" | "" | None:
            return None
        case str():
            return Path(value)
        case Path():
            return value
        case _:
            raise ValueError(f"Invalid value {value}")  # pyright: ignore[reportUnreachable]


class PathConfigParserProperty(SubscriptableConfigParserProperty[Path | None]):
    def __init__(
        self, default: Path | None, section: str, key: str, config_name: str = "app"
    ) -> None:
        super().__init__(
            default, section, key, config_name, val_type=_to_path, errorvalue=None
        )

    def set(self, obj: EventDispatcher, value: Path | str | None) -> bool:
        val = "" if value is None else str(value)

        if val not in {"None", "null", ""}:
            Path(val).mkdir(parents=True, exist_ok=True)

        return super().set(obj, val)
