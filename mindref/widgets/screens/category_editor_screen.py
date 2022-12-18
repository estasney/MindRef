from typing import TYPE_CHECKING

from kivy.event import EventDispatcher

e = EventDispatcher()
from utils import import_kv
from widgets.screens import InteractScreen

if TYPE_CHECKING:
    pass

import_kv(__file__)


class CategoryEditorScreen(InteractScreen):
    ...
