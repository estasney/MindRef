from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from mindref.lib import get_app


class SettingsScreen(Screen):
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = get_app()
