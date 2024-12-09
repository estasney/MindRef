from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout

from mindref.lib.utils import import_kv
from mindref.lib.widgets.buttons.category import NoteCategoryButton

import_kv(__file__)


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

    def draw_categories(self, *_args):
        container = self.category_container

        screen_categories = set(child.text for child in container.children)
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
