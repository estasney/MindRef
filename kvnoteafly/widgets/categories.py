from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.properties import (
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from utils import import_kv

import_kv(__file__)


class CategoryScreenScrollWrapper(ScrollView):
    """Screen With Buttons for Categories"""

    manager = ObjectProperty()
    chooser = ObjectProperty()
    categories = ListProperty()

    def category_selected(self, instance: "NoteCategoryButton"):
        self.manager.category_selected(instance)


class NoteCategories(BoxLayout):
    category_container = ObjectProperty()
    categories = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fbind = self.fbind
        fbind("categories", self.handle_categories)

    def category_callback(self, instance: "NoteCategoryButton"):
        self.parent.category_selected(instance)

    def handle_categories(self, instance, value):
        Clock.schedule_once(
            partial(self.clear_categories, callback=self.draw_categories)
        )

    def clear_categories(self, dt, callback):
        self.category_container.clear_widgets()
        if callback:
            Clock.schedule_once(callback)

    def draw_categories(self, dt):
        for category in self.categories:
            cat_btn = NoteCategoryButton(text=category)
            cat_btn.bind(on_release=self.category_callback)
            self.category_container.add_widget(cat_btn)


class NoteCategoryButton(ButtonBehavior, BoxLayout):
    source = StringProperty()
    text = StringProperty()
    image = ObjectProperty()
    tx_bg_normal = ObjectProperty()
    tx_bg_down = ObjectProperty()

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.source = App.get_running_app().atlas_service.uri_for(
            text.lower(), "category_img"
        )
        self.text = text
        self.load_texture("bg_normal")
        self.load_texture("bg_down")

    def load_texture(self, name):
        get_uri = App.get_running_app().atlas_service.uri_for
        get_region = App.get_running_app().atlas_service.region_for

        img = Image(get_uri(name.lower(), "textures"))
        region = get_region(name.lower(), "textures")
        texture = img.texture
        texture = texture.get_region(*region)
        setattr(self, f"tx_{name}", texture)
