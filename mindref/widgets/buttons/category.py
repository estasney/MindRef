from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.loader import Loader
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout


class NoteCategoryButton(ButtonBehavior, BoxLayout):
    source = StringProperty()
    text = StringProperty()
    image = ObjectProperty()
    tx_bg_normal = ObjectProperty()
    tx_bg_down = ObjectProperty()
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
            str(uri)
            if (uri := App.get_running_app().note_service.category_image_uri(text))
            else ""
        )
        self.text = text
        self.load_texture("bg_normal")
        self.load_texture("bg_down")

    def load_texture(self, name):
        get_uri = App.get_running_app().atlas_service.uri_for
        img = Image(get_uri(name.lower(), "textures"))
        tx = img.texture
        setattr(self, f"tx_{name}", tx)

    def category_tx_loaded(self, *args):
        self.tx_category = self.img_loader.texture

    def load_category_texture(self, *args):
        if self.img_loader is None:
            self.img_loader = Loader.image(self.source)
        if self.img_loader.loaded:
            self.tx_category = self.img_loader.texture
        else:
            self.img_loader.bind(on_load=lambda x: self.set_category_tx_trigger())
