import abc
from abc import ABC


class AtlasServiceProtocol(ABC):
    @abc.abstractmethod
    def get_from_atlas(self, name: str, atlas_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def save_to_atlas(self, img, name: str, atlas_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def uri_for(self, name: str, atlas_name: str) -> str:
        """Return URI for Kivy"""
        raise NotImplementedError
