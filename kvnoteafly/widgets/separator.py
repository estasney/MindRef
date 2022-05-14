from kivy.properties import ColorProperty
from kivy.uix.widget import Widget
from kivy.app import App
from utils import import_kv

import_kv(__file__)


class Separator(Widget):
    color = ColorProperty(App.get_running_app().colors["Dark"])


class HSeparator(Separator):
    ...


class VSeparator(Separator):
    ...
