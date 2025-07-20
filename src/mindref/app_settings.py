from __future__ import annotations

from pathlib import Path

from kivy.properties import (
    ConfigParserProperty,
)


def _to_path(value: str | Path | None) -> Path | None:
    if value in {"None", "null", "", None}:
        return None
    return Path(value)


class PathConfigParserProperty(ConfigParserProperty):
    # noinspection PyArgumentList
    def __init__(
        self, default: Path | None, section: str, key: str, config_name: str = "app"
    ):
        super().__init__(
            default, section, key, config_name, val_type=_to_path, errorvalue=None
        )

    def set(self, EventDispatcher_obj, value):
        val = "" if value is None else str(value)

        if val not in {"None", "null", ""}:
            Path(val).mkdir(parents=True, exist_ok=True)

        super().set(EventDispatcher_obj, val)
