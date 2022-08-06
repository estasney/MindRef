from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from utils import import_kv
from widgets.effects.scrolling import RefreshOverscrollEffect

import_kv(__file__)


class CategoryScreenScrollWrapper(ScrollView):
    """Screen With Buttons for Categories"""

    screen = ObjectProperty()
    chooser = ObjectProperty()
    refresh_triggered = BooleanProperty(False)

    effect_cls = RefreshOverscrollEffect

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_chooser(self, instance, value):
        self.chooser.bind(minimum_height=self.chooser.setter("height"))

    def on_screen(self, instance, value):
        self.bind(refresh_triggered=self.screen.setter("refresh_triggered"))

    def category_selected(self, instance: "NoteCategoryButton"):
        self.screen.category_selected(instance)


class NoteCategories(BoxLayout):
    category_container = ObjectProperty()
    categories = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fbind = self.fbind
        self.draw_categories_trigger = Clock.create_trigger(self.draw_categories)
        fbind("categories", self.draw_categories_trigger)

    def category_callback(self, instance: "NoteCategoryButton"):
        self.parent.category_selected(instance)

    def draw_categories(self, dt):

        container = self.category_container

        screen_categories = set((child.text for child in container.children))
        prop_categories = set(self.categories)

        remove_categories = screen_categories - prop_categories
        add_categories = prop_categories - screen_categories

        # Removal
        for r_cat in remove_categories:
            matched_btn = next(
                (child for child in container.children if child.text == r_cat), None
            )
            if not matched_btn:
                continue
            container.remove_widget(matched_btn)

        # Addition
        for a_cat in add_categories:
            cat_btn = NoteCategoryButton(text=a_cat)
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
        img = Image(get_uri(name.lower(), "textures"))
        tx = img.texture
        setattr(self, f"tx_{name}", tx)
