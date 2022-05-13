from __future__ import annotations

import abc
from abc import ABC
from pathlib import Path
from typing import Optional, Sequence


class AtlasServiceProtocol(ABC):
    @abc.abstractmethod
    def get_from_atlas(self, name: str, atlas_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def save_to_atlas(
        self,
        images: Sequence[Path | str],
        image_names: Sequence[str],
        atlas_name: str,
        atlas_size: Optional[tuple[int, int]] = None,
        padding=2,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def uri_for(self, name: str, atlas_name: str) -> str:
        """Return URI for Kivy"""
        raise NotImplementedError
