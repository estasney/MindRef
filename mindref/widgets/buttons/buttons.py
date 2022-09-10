from pathlib import Path
from kivy.properties import ColorProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from utils import import_kv, mindref_path

texture_atlas = "atlas://" + str(mindref_path() / "static" / "textures" / "textures")
import_kv(__file__)


class HamburgerIcon(BoxLayout):
    release_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super(HamburgerIcon, self).__init__(**kwargs)


class TexturedButton(ButtonBehavior, BoxLayout):
    background_normal = StringProperty(f"{texture_atlas}/bg_normal")
    background_down = StringProperty(f"{texture_atlas}/bg_down")
    background_color = ColorProperty()

    def __init__(self, **kwargs):
        super(TexturedButton, self).__init__(**kwargs)
