from kivy.properties import (
    ColorProperty,
    DictProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv, mindref_path, get_app

texture_atlas = "atlas://" + str(mindref_path() / "static" / "textures" / "textures")
icon_atlas = "atlas://" + str(mindref_path() / "static" / "icons" / "icons")
import_kv(__file__)


class HamburgerIcon(BoxLayout):
    release_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(HamburgerIcon, self).__init__(**kwargs)


class TexturedButton(ButtonBehavior, BoxLayout):
    background_normal = StringProperty(f"{texture_atlas}/bg_normal")
    background_down = StringProperty(f"{texture_atlas}/bg_down")
    background_color = ColorProperty()
    border_size = VariableListProperty()

    def __init__(self, **kwargs):
        super(TexturedButton, self).__init__(**kwargs)


class TexturedLabelButton(TexturedButton):
    text: StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ImageButton(TexturedButton):
    source = StringProperty()

    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)


class BackButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/back")

    def __init__(self, **kwargs):
        super(BackButton, self).__init__(**kwargs)


class ForwardButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/forward")

    def __init__(self, **kwargs):
        super(ForwardButton, self).__init__(**kwargs)


class EditButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/edit")

    def __init__(self, **kwargs):
        super(EditButton, self).__init__(**kwargs)


class SaveButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/save")

    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)


class CancelButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/cancel")

    def __init__(self, **kwargs):
        super(CancelButton, self).__init__(**kwargs)


class AddButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/add")

    def __init__(self, **kwargs):
        super(AddButton, self).__init__(**kwargs)


class FileButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/file")

    def __init__(self, **kwargs):
        super(FileButton, self).__init__(**kwargs)


class PlayStateButton(ImageButton):
    source = StringProperty(f"{icon_atlas}/play")
    icon_active = OptionProperty("play", options=["play", "pause"])
    sources = DictProperty(
        {"play": f"{icon_atlas}/play", "pause": f"{icon_atlas}/pause"}
    )

    def __init__(self, **kwargs):
        super(PlayStateButton, self).__init__(**kwargs)
        app = get_app()
        app.bind(play_state=self.handle_play_state)

    def handle_icon_active(self, *_args):
        self.source = self.sources[self.icon_active]

    def handle_play_state(self, instance, _):
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
