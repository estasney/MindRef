from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import RenderContext, Color, Rectangle
from kivy.loader import Loader
from kivy.properties import ObjectProperty, StringProperty

from utils import import_kv, get_app
from widgets.buttons.buttons import ThemedButton
from widgets.effects.ripple import RippleMixin

import_kv(__file__)


class NoteCategoryButton(ThemedButton, RippleMixin):
    source = StringProperty()
    text = StringProperty()
    image = ObjectProperty()
    tx_category = ObjectProperty(Loader.loading_image.texture)

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)

        self.img_loader = None
        self.load_category_tx_trigger = Clock.create_trigger(self.load_category_texture)
        self.set_category_tx_trigger = Clock.create_trigger(
            self.category_tx_loaded, timeout=0.1
        )
        self.fbind("source", self.load_category_tx_trigger)
        self.source = (
            str(uri) if (uri := get_app().note_service.category_image_uri(text)) else ""
        )
        self.text = text

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            self.touch = touch.spos

            self.no_touch_trigger.cancel()
            self.has_touch_trigger()
            return True
        return False

    def on_touch_move(self, touch):
        if super().on_touch_move(touch):
            self.touch = touch.spos
            return True
        return False

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        self.has_touch_trigger.cancel()
        self.no_touch_trigger()
        return True

    def category_tx_loaded(self, *_args):
        self.tx_category = self.img_loader.texture

    def load_category_texture(self, *_args):
        if self.img_loader is None:
            self.img_loader = Loader.image(self.source)
        if self.img_loader.loaded:
            self.tx_category = self.img_loader.texture
        else:
            self.img_loader.bind(on_load=lambda x: self.set_category_tx_trigger())
