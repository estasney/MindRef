from __future__ import annotations
from typing import NamedTuple
from pathlib import Path

from services.atlas import AtlasServiceProtocol
from services.utils import LazyLoaded


class AtlasItem(NamedTuple):
    name: str
    path: Path


class AtlasService(AtlasServiceProtocol):
    """
    Manages Atlases
    - Storage Location
    - Inserting and Removing
    - Provides path for kivy usage
    """

    atlases: list[AtlasItem] = LazyLoaded()

    def __init__(self, storage_path: str | Path):
        self.storage_page = Path(storage_path)
        self._atlases = None

    @atlases
    def _discover_atlases(self):
        atlas = []
        for item in self.storage_page.iterdir():
            if item.is_dir():
                if af := next(item.glob(f"*.atlas"), None):
                    atlas.append(AtlasItem(item.stem, af))
        return atlas

    def save_to_atlas(self, img, name: str, atlas_name: str):
        pass

    def get_from_atlas(self, name: str, atlas_name: str):
        pass

    def uri_for(self, name: str, atlas_name: str):
        try:
            matched = next(
                (atlas for atlas in self.atlases if atlas.name == atlas_name)
            )
        except StopIteration:
            raise KeyError(f"{atlas_name} not found")
        return f"atlas://{matched.path.with_suffix('')}/{name}"
