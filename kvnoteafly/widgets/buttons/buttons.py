from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    DictProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from utils import import_kv
from widgets.mixins import TrackParentPadding

import_kv(__file__)


def get_uri(name):
    return App.get_running_app().atlas_service.uri_for(name, atlas_name="icons")


class ImageButton(ButtonBehavior, Image, TrackParentPadding):
    def __init__(self, src, *args, **kwargs):
        super().__init__()
        self.source = src


class DynamicImageButton(ImageButton):
    sources = DictProperty()

    def __init__(self, sources: list[str], **kwargs):
        self.sources = {k: get_uri(k) for k in sources}
        super().__init__(**{**{"src": self.sources[sources[0]]}, **kwargs})


class PlayStateButton(DynamicImageButton):
    playing = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.fbind("playing", self.handle_play_state)
        app_state = App.get_running_app().play_state
        src = "play" if app_state == "pause" else "pause"
        super().__init__(
            sources=["play", "pause"],
            **kwargs,
        )
        self.source = self.sources[src]

    def handle_play_state(self, instance, value):
        app = App.get_running_app()
        app.play_state = "play" if self.playing else "pause"
        self.source = self.sources["pause"] if self.playing else self.sources["play"]
        return True


class BackButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src=get_uri("back"))


class ForwardButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src=get_uri("forward"))


class ReturnButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src=get_uri("back_arrow"))


class ListViewButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src=get_uri("list_view"))


class EditButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super(EditButton, self).__init__(src=get_uri("edit"))


class SaveButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super(SaveButton, self).__init__(src=get_uri("save"))


class CancelButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super(CancelButton, self).__init__(src=get_uri("cancel"))


class AddButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super(AddButton, self).__init__(src=get_uri("add"))
