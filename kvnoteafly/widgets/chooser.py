from kivy.app import App
from kivy.core.window import Window
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.vector import Vector

from utils import import_kv
from widgets.mixins import TrackParentPadding

import_kv(__file__)


class NoteCategoryChooserScrollWrapper(ScrollView):
    manager = ObjectProperty()
    child_object = ObjectProperty()
    categories = ListProperty()

    def category_selected(self, instance: "NoteCategoryButton"):
        self.manager.category_selected(instance)

    def on_categories(self, instance, value):
        if not self.children:
            layout = NoteCategoryChooser(size_hint=(1, None), width=Window.width)
            layout.bind(minimum_height=layout.setter("height"))
            self.add_widget(layout)
            self.child_object = layout
            self.children[0].set(value)


class NoteCategoryChooser(GridLayout):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_parent(self, *args, **kwargs):
        self.manager = args[1]

    def category_callback(self, instance: "NoteCategoryButton"):
        self.manager.category_selected(instance)

    def set(self, value):
        category_widgets = [
            NoteCategoryButton(text=cat, size_hint=(0.25, None)) for cat in value
        ]
        for cat in category_widgets:
            cat.bind(on_release=self.category_callback)
            self.add_widget(cat)


class NoteCategoryButton(ButtonBehavior, BoxLayout, TrackParentPadding):
    source = StringProperty()
    text = StringProperty()

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.source = App.get_running_app().atlas_service.uri_for(
            text.lower(), "category_img"
        )
        self.text = text
