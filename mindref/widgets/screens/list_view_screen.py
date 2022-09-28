from kivy.properties import ObjectProperty

from utils import import_kv
from widgets.screens import InteractScreen

import_kv(__file__)


class NoteListViewScreen(InteractScreen):
    list_view_bar = ObjectProperty()
