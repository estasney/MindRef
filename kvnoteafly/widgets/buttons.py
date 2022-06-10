from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from utils import import_kv
from widgets.mixins import TrackParentPadding

import_kv(__file__)


def get_uri(name):
    return App.get_running_app().atlas_service.uri_for(name, atlas_name="icons")


class ButtonBar(BoxLayout):
    ...


class ImageButton(ButtonBehavior, Image, TrackParentPadding):
    def __init__(self, src, *args, **kwargs):
        super().__init__()
        self.source = src


class DynamicImageButton(ButtonBehavior, Image):
    sources = ListProperty([])

    def __init__(self, sources: list[str], **kwargs):
        super().__init__(**kwargs)
        self.sources = sources
        if "source" in kwargs:
            self.source = kwargs.pop("source")
        else:
            self.source = self.sources[0]


class PlayStateButton(DynamicImageButton):
    sources = ListProperty([])
    playing = BooleanProperty(True)
    color = ColorProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        self.fbind("playing", self.handle_play_state)

        app_state = App.get_running_app().play_state
        src = "play" if app_state == "pause" else "pause"
        super().__init__(
            source=get_uri(src),
            sources=[get_uri("play"), get_uri("pause")],
            **kwargs,
        )

    def handle_play_state(self, instance, value):
        app = App.get_running_app()
        app.play_state = "play" if self.playing else "pause"
        self.source = self.sources[1] if self.playing else self.sources[0]
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
