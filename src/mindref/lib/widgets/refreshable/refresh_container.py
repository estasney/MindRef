from kivy.animation import Animation
from kivy.core.window import Window
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    Clock,
    NumericProperty,
    VariableListProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from ...ext import compute_overscroll
from . import V2RefreshBehavior


class RefreshScrollView(V2RefreshBehavior, ScrollView):
    overscroll_progress = NumericProperty(0.0)
    refresh_threshold = NumericProperty(
        0.8
    )  # how far to pull (0..1) to trigger refresh

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect_y = OpacityScrollEffect()


Builder.load_string(
    """
#:import RefreshSymbol mindref.lib.widgets.effects.scrolling.RefreshSymbol
#:import RefreshOverscrollEffect mindref.lib.widgets.effects.scrolling.RefreshOverscrollEffect
#:import OpacityScrollEffect kivy.effects.opacityscroll.OpacityScrollEffect
<V2RefreshContainer>:
    scroll_view: scroll_view
    item_spacing: [0, 0]
    item_padding: [0, 0, 0, 0]
    FloatLayout:
        id: float_layout
        RefreshSymbol:
            rotation: root.overscroll_progress * 360  # rotate based on overscroll progress
            animate: root.refreshing  # animate if refreshing
            id: refresh_symbol
            pos_hint: {"center_x": 0.5, "top": 1 -  (root.overscroll_progress / 4)}  # center vertically based on overscroll
            opacity: root.overscroll_progress if not root.refreshing else 1  # fully visible if refreshing
    RelativeLayout:
        pos_hint: {"center_x": 0.5, "y": 0}
        size_hint_x: None
        width: root.width
        RefreshScrollView:
            id: scroll_view
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: main
                spacing: root.item_spacing
                padding: root.item_padding
                cols: 1
                size_hint_y: None
                height: self.minimum_height
    """
)


class V2RefreshContainer(FloatLayout, V2RefreshBehavior):
    """
    This widget implements a ScrollView contained in a RelativeLayout. This nesting of layouts is necessary so that the Refresh icon
    can be positioned in the center of the screen. The ScrollView is used to enable the overscroll effect for refreshing.
    """

    item_spacing = VariableListProperty([0, 0], length=2)
    item_padding = VariableListProperty([0, 0, 0, 0])
    overscroll_progress = NumericProperty(0.0)
    refresh_threshold = NumericProperty(0.25)
    refreshing = BooleanProperty(False)
    animate_icon_hide: Animation

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(
            self._bind_scroll_effect, 0
        )  # bind scroll effect after layout is ready

    def _bind_scroll_effect(self, _dt):
        effect = self.ids.scroll_view.effect_y
        effect.bind(overscroll=self._on_overscroll_value)

    def _on_overscroll_value(self, effect, value):
        if effect.is_manual:
            self.overscroll_progress = compute_overscroll(
                value, Window.height, self.refresh_threshold
            )
            return
        if self.overscroll_progress == 1:
            self.refreshing = True
            self.dispatch("on_refresh", self, True)
            self.overscroll_progress = 0
        else:
            Animation(overscroll_progress=0, d=0.2).start(self)

    def on_overscroll_progress(self, _widget, value):
        """
        Called when the overscroll progress changes.
        This can be used to update the refresh icon or trigger a refresh.
        """
        ...

    def add_widget_to_main(self, widget: Widget):
        """
        Add a widget to the grid layout
        :param widget: The widget to add
        """
        if not self.ids.main:
            Logger.error(f"{type(self).__name__} : No grid layout found")
            return
        widget.padding = self.item_padding
        self.ids.main.add_widget(widget)

    def clear_widgets_from_main(self):
        """
        Clear all widgets from the grid layout
        """
        if not self.ids.main:
            Logger.error(f"{type(self).__name__} : No grid layout found")
            return
        self.ids.main.clear_widgets()

    def main_children(self):
        return self.ids.main.children

    def on_overscroll(self, *args):
        Logger.info(f"{type(self).__name__} : on_overscroll called with args: {args}")


__all__ = [
    "V2RefreshContainer",
]
