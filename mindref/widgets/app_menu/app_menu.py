from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.modalview import ModalView

from utils import import_kv

import_kv(__file__)


class AppMenu(ModalView):
    platform_android = BooleanProperty()
    btnroot = ObjectProperty()
    br = ObjectProperty()

    def __init__(self, **kwargs):
        super(AppMenu, self).__init__(**kwargs)
