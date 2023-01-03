from kivy.properties import (
    ColorProperty,
    ObjectProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv, mindref_path

texture_atlas = "atlas://" + str(mindref_path() / "static" / "textures" / "textures")
icon_atlas = "atlas://" + str(mindref_path() / "static" / "icons" / "icons")
import_kv(__file__)


class HamburgerIcon(BoxLayout):
    release_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(HamburgerIcon, self).__init__(**kwargs)


class ThemedButton(ButtonBehavior, BoxLayout):
    background_normal = StringProperty(f"{texture_atlas}/bg_normal")
    background_down = StringProperty(f"{texture_atlas}/bg_down")
    background_disabled = StringProperty(f"{texture_atlas}/bg_disabled")
    background_color = ColorProperty()
    border_size = VariableListProperty()

    def __init__(self, **kwargs):
        super(ThemedButton, self).__init__(**kwargs)


class ThemedLabelButton(ThemedButton):
    text: StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ImageButton(ThemedButton):
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
