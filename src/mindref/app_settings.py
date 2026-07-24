from __future__ import annotations

from pathlib import Path

from kivy.properties import (
    ConfigParserProperty,
)


def _to_path(value: str | Path | None) -> Path | None:
    match value:
        case "None" | "null" | "" | None:
            return None
        case str():
            return Path(value)
        case Path():
            return value
        case _:
            raise ValueError(f"Invalid value {value}")


class PathConfigParserProperty(ConfigParserProperty):
    def __init__(
        self, default: Path | None, section: str, key: str, config_name: str = "app"
    ):
        super().__init__(
            default, section, key, config_name, val_type=_to_path, errorvalue=None
        )

    def set(self, EventDispatcher, value):
        val = "" if value is None else str(value)

        if val not in {"None", "null", ""}:
            Path(val).mkdir(parents=True, exist_ok=True)

        super().set(EventDispatcher, val)
