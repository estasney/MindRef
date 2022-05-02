from operator import itemgetter

from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivy.vector import Vector
from kivy import Logger
from utils import import_kv

import_kv(__file__)


class ButtonBar(BoxLayout):

    last_touched = ObjectProperty()

    def on_touch_down(self, touch):
        """
        These buttons tend to overlap. To avoid pressing multiple, we dispatch the event to the 'closest' button
        """
        if not self.collide_point(*touch.pos):
            Logger.debug("Touch outside")
            return
        if touch.is_double_tap:
            Logger.debug("Double Tap")
        collides = [
            (child, child.touch_offset(*touch.pos))
            for child in self.children[:]
            if hasattr(child, "touch_offset")
        ]
        if not any(collides):
            # Shouldn't happen
            Logger.debug("No Collides Found")
            return

        # Find closest
        child = min(collides, key=itemgetter(1))[0]
        child.dispatch("on_touch_down", touch)
        Logger.debug(f"Found Closest, {child}")
        self.last_touched = child
        return True

    def on_touch_up(self, touch):
        if self.last_touched:
            Logger.debug(f"Calling Last Touched {self.last_touched}")
            result = self.last_touched.dispatch("on_touch_up", touch)
            return result


class RoundedButton(Button):
    DISABLED_COLOR = get_color_from_hex("#9e9ea2")
    FONT_COLOR = get_color_from_hex("#ffffff")

    def collide_point(self, x, y):
        return Vector(x, y).distance(self.center) <= self.width / 2


class RedButton(RoundedButton):
    UNPRESSED_COLOR = StringProperty(get_color_from_hex("#ff000d"))
    PRESSED_COLOR = StringProperty(get_color_from_hex("#be0119"))


class GreenButton(RoundedButton):
    UNPRESSED_COLOR = StringProperty(get_color_from_hex("#21fc0d"))
    PRESSED_COLOR = StringProperty(get_color_from_hex("#048243"))
    FONT_COLOR = StringProperty(get_color_from_hex("#000000"))


class ImageButton(ButtonBehavior, Image):
    def __init__(self, src, *args, **kwargs):
        super().__init__()
        self.source = src

    def touch_offset(self, x, y) -> tuple[float, float]:
        distance = Vector(x, y).distance(self.center)
        return distance, self.norm_image_size[0] / 2

    def collide_point(self, x, y):
        distance = Vector(x, y).distance(self.center)
        return distance <= self.norm_image_size[0] / 2


class DynamicImageButton(ButtonBehavior, Image):
    sources = ListProperty([])

    def __init__(self, sources: list[str], **kwargs):
        super().__init__(**kwargs)
        self.sources = sources
        if "source" in kwargs:
            self.source = kwargs.pop("source")
        else:
            self.source = self.sources[0]

    def touch_offset(self, x, y) -> tuple[float, float]:
        distance = Vector(x, y).distance(self.center)
        return distance, self.norm_image_size[0] / 2

    def collide_point(self, x, y):
        distance = Vector(x, y).distance(self.center)
        return distance <= self.norm_image_size[0] / 2


class PlayStateButton(DynamicImageButton):
    sources = ListProperty([])
    playing = BooleanProperty(True)
    color = ColorProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(
            source="atlas://static/icons/button_bar/play",
            sources=[
                "atlas://static/icons/button_bar/play",
                "atlas://static/icons/button_bar/pause",
            ],
            **kwargs,
        )
        App.get_running_app().bind()

    def toggle_play_state(self):
        app = App.get_running_app()
        app.play_state = "pause" if app.play_state == "play" else "play"

    def on_playing(self, _old, new):
        self.source = self.sources[0] if new else self.sources[1]
        self.color = [1, 1, 1, 1] if new else [0.86666, 0.247, 0.0627, 1]


class BackButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src="atlas://static/icons/button_bar/back")


class ForwardButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src="atlas://static/icons/button_bar/forward")


class ReturnButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src="atlas://static/icons/button_bar/back_arrow")


class ListViewButton(ImageButton):
    def __init__(self, *args, **kwargs):
        super().__init__(src="atlas://static/icons/button_bar/list_view")
