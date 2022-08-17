from kivy.app import App
from kivy.properties import (
    DictProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
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
    icon_active = OptionProperty("play", options=["play", "pause"])

    def __init__(self, **kwargs):
        super().__init__(
            sources=["play", "pause"],
            **kwargs,
        )
        app = App.get_running_app()
        app.bind(play_state=self.handle_play_state)
        self.handle_play_state(app, app.play_state)
        self.bind(icon_active=self.handle_icon_active)

    def handle_icon_active(self, instance, value):
        self.source = self.sources[self.icon_active]

    def handle_play_state(self, instance, value):
        """When App's play_state is 'pause', we show a play icon"""
        if instance.play_state == "pause":
            self.icon_active = "play"

        else:
            self.icon_active = "pause"

    def handle_press(self, app):
        """
        Our source of truth for whether the app is 'paused' or 'playing' is self.
        """
        app.play_state_trigger(self.icon_active)


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


class HamburgerIcon(BoxLayout):
    release_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(HamburgerIcon, self).__init__(**kwargs)
