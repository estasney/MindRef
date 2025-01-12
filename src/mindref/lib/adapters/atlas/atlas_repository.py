import abc
from collections.abc import Sequence
from pathlib import Path

import PIL.Image


class AbstractAtlasRepository(abc.ABC):
    @abc.abstractmethod
    def get_from_atlas(self, name: str, atlas_name: str) -> PIL.Image:
        raise NotImplementedError

    @abc.abstractmethod
    def save_to_atlas(
        self,
        images: Sequence[Path | str],
        image_names: Sequence[str],
        atlas_name: str,
        atlas_size: tuple[int, int] | None = None,
        padding: int = 2,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def uri_for(self, name: str, atlas_name: str) -> str:
        """Return URI for Image"""
        raise NotImplementedError
