from kivy import Logger
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.metrics import sp
from kivy.modules import inspector
from kivy.modules.inspector import Inspector
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget


class CustomBehavior:
    """
    Base class for custom behaviors.

    Event types are
    """

    __custom_events__ = frozenset({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for event in self.__custom_events__:
            self.register_event_type(event)


class DebugLayout(Layout):
    """
    This subclass will add a new property, `debug_layout`

    If True, then it will draw a rectangle around the widget using red.
    """

    debug_layout = BooleanProperty(False)
    outline = ObjectProperty(None, rebind=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fbind = self.fbind
        update_debug_layout = self.update_debug_layout
        fbind("children", update_debug_layout)
        fbind("pos", update_debug_layout)
        fbind("pos_hint", update_debug_layout)
        fbind("size_hint", update_debug_layout)
        fbind("size", update_debug_layout)
        fbind("debug_layout", update_debug_layout)
        fbind("on_debug_layout", update_debug_layout)

    def update_debug_layout(self, instance, value):
        if self.debug_layout:
            if self.outline:
                self.canvas.remove(self.outline)
            outline = InstructionGroup()
            outline.add(Color(1, 0, 0, 1))
            outline.add(
                Line(rectangle=(self.x, self.y, self.width, self.height), width=sp(1))
            )
            Logger.info(
                f"DebugLayout: {self} - {self.x}, {self.y}, {self.width}, {self.height}"
            )
            self.outline = outline
            self.canvas.add(outline)
            self.canvas.ask_update()


class DebugGridLayout(GridLayout, DebugLayout): ...


class DebugFloatLayout(FloatLayout, DebugLayout): ...


class DebugBoxLayout(BoxLayout, DebugLayout):
    """
    A BoxLayout that supports debugging features.
    It inherits from DebugLayout to provide debugging capabilities.
    """

    pass
