from __future__ import annotations

from kivy.graphics import Color, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.logger import Logger
from kivy.metrics import sp
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget


class CustomBehavior(Widget): ...


class DebugLayout(Layout):
    """
    This subclass will add a new property, `debug_layout`

    If True, then it will draw a rectangle around the widget using red.
    """

    debug_layout = BooleanProperty(False)
    outline: ObjectProperty[InstructionGroup | None] = ObjectProperty(None, rebind=True)

    def __init__(self, **kwargs: object):
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

    def update_debug_layout(self, _instance: DebugLayout, _value: object) -> None:
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
