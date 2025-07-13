from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, Literal, NamedTuple

from kivy import Logger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.floatlayout import FloatLayout

from mindref.lib.models import AnimationTiming
from mindref.lib.widgets.behavior import DebugLayout
from mindref.lib.widgets.buttons.buttons import ThemedIconButton
from mindref.lib.widgets.nav_drawer.nav_item import NavItem, NavItemData
from mindref.lib.widgets.nav_drawer.search_box import SearchBox
from mindref.lib.widgets.refreshable import V2RefreshBehavior, V2RefreshContainer

if TYPE_CHECKING:
    from kivy.uix.boxlayout import BoxLayout


class OpenState(str, Enum):
    open = "open"
    opening = "opening"
    closed = "closed"
    closing = "closing"

    def __str__(self) -> str:
        return str.__str__(self)


TOpenState = Literal["open", "opening", "closed", "closing"]
TAnimatedProperty = Literal[
    "size_hint_x_closed",
    "size_hint_x_open",
    "animation_open_duration",
    "animation_open_timing",
    "animation_closed_duration",
    "animation_closed_timing",
]

Builder.load_string(
    """
#:import ThemedMenuButton mindref.lib.widgets.buttons
#:import V2RefreshContainer mindref.lib.widgets.refreshable.refresh_container
#:import DebugGridLayout mindref.lib.widgets.behavior.DebugGridLayout
<NavDrawer>:
    id: nav_drawer
    pos_hint: {"left": 0}
    nav_link_padding: [dp(0), dp(12), dp(0), dp(12)]
    nav_link_spacing: [dp(0), dp(0)]
    debug_layout: False
    BoxLayout:
        orientation: "horizontal"
        id: top_bar
        pos_hint: {"top": 1}
        size_hint_y: 0.1
        padding: [dp(5), 0, 0, 0]
        OpenMenuButton:
            id: menu_button
            on_release: root.toggle(self)
            pos_hint: root._menu_button_pos_hint_closed
            width: self.height
            size_hint: None, None
    V2RefreshContainer:
        id: nav_items
        item_spacing: root.nav_link_spacing
        item_padding: root.nav_link_padding
        size_hint_y: 0.9
        pos_hint: {"top": 0.9}
        opacity: 0
        
"""
)


class NavDrawerIds(NamedTuple):
    top_bar: "BoxLayout"
    menu_button: "ThemedIconButton"
    nav_items: "V2RefreshContainer"


class NavDrawer(FloatLayout, DebugLayout, V2RefreshBehavior):
    ids: NavDrawerIds = DictProperty({})
    size_hint_x_closed = NumericProperty(0)
    size_hint_x_open = NumericProperty(0)
    size_hint_x = NumericProperty(0, allownone=False)
    animation_open_duration = NumericProperty(0.2)
    animation_open_timing = OptionProperty(
        AnimationTiming.in_out_quad, options=[AnimationTiming.__members__.values()]
    )
    animation_closed_duration = NumericProperty(0.2)
    animation_closed_timing = OptionProperty(
        AnimationTiming.in_out_quad, options=[AnimationTiming.__members__.values()]
    )

    animation_close_duration = NumericProperty(0.2)
    open_state = OptionProperty(
        OpenState.closed, options=list(OpenState.__members__.values())
    )

    clear_search_button = ObjectProperty(allownone=True)
    search_box: SearchBox | None = ObjectProperty(allownone=True)
    search_filter: str = StringProperty("")

    drawer_open_animation: Animation
    drawer_close_animation: Animation
    fade_in_animation: Animation
    fade_out_animation: Animation

    nav_link_spacing = VariableListProperty([0, 0], length=2)
    nav_link_padding = VariableListProperty([0, 0, 0, 0], length=4)
    nav_data_items: list[NavItemData] = ListProperty([])
    nav_id_selected = StringProperty(None, allownone=True)
    close_on_nav = BooleanProperty(True)

    _menu_button_pos_hint_closed = DictProperty({"center_x": 0.5, "center_y": 0.5})
    _menu_button_pos_hint_open = DictProperty({"left": 0, "center_y": 0.5})
    _search_filter_sch_event: None

    __events__ = (
        "on_open",
        "on_close",
        "on_opening",
        "on_closing",
        "on_nav_selected",
        "on_search_clear",
        "on_refresh",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawer_open_animation = Animation(
            size_hint_x=self.size_hint_x_open,
            duration=self.animation_open_duration,
            t=self.animation_open_timing,
        )
        self.drawer_open_animation.bind(on_complete=self.open_state_open_cb)
        self.drawer_close_animation = Animation(
            size_hint_x=self.size_hint_x_closed,
            duration=self.animation_closed_duration,
            t=self.animation_closed_timing,
        )
        self.drawer_close_animation.bind(on_complete=self.open_state_closed_cb)
        self.fade_in_animation = Animation(
            opacity=1,
            duration=self.animation_open_duration,
            t=self.animation_open_timing,
        )
        self.fade_out_animation = Animation(
            opacity=0,
            duration=self.animation_closed_duration,
            t=self.animation_closed_timing,
        )

        self.fbind(
            "size_hint_x_closed", self.handle_animation_change, "size_hint_x_closed"
        )
        self.fbind("size_hint_x_open", self.handle_animation_change, "size_hint_x_open")
        self.fbind(
            "animation_open_duration",
            self.handle_animation_change,
            "animation_open_duration",
        )
        self.fbind(
            "animation_open_timing",
            self.handle_animation_change,
            "animation_open_timing",
        )
        self.fbind(
            "animation_closed_duration",
            self.handle_animation_change,
            "animation_closed_duration",
        )
        self.fbind(
            "animation_closed_timing",
            self.handle_animation_change,
            "animation_closed_timing",
        )
        self._search_filter_sch_event = None
        self.trigger_search_filter = Clock.create_trigger(self._dispatch_search_filter)

    def open_state_open_cb(self, *args, **kwargs):
        Logger.debug(
            f"{type(self).__name__} : open_state_open_cb called with args: {args}, kwargs: {kwargs}"
        )
        self.open_state = OpenState.open
        self.ids.nav_items.refresh_enabled = True

    def open_state_closed_cb(self, *args, **kwargs):
        Logger.debug(
            f"{type(self).__name__} : open_state_closed_cb called with args: {args}, kwargs: {kwargs}"
        )
        self.open_state = OpenState.closed
        self.ids.nav_items.refresh_enabled = False

    def attach_search_box(self):
        if self.search_box is None:
            self.search_box = SearchBox(pos_hint={"center_y": 0.5}, hint_text="Search")
            self.search_box.bind(text=self.setter("search_filter"))
            self.ids.top_bar.add_widget(self.search_box)
        if self.clear_search_button is None:
            self.clear_search_button = ThemedIconButton(
                icon_code="\ue5cd",
                size_hint=(None, None),
                opacity=0,
                background_color=(0, 0, 0, 0),
                color=(1.0, 1.0, 1.0, 0.5),
                pos_hint={"center_y": 0.5},
            )
            self.clear_search_button.bind(
                height=self.clear_search_button.setter("width"),
                on_release=lambda _: self.dispatch(
                    "on_search_clear", self.clear_search_button
                ),
            )
            self.ids.top_bar.add_widget(self.clear_search_button)

    def detach_search_box(self):
        if self.clear_search_button is not None:
            self.ids.top_bar.remove_widget(self.clear_search_button)
            self.clear_search_button = None
        if self.search_box is not None:
            self.ids.top_bar.remove_widget(self.search_box)
            self.search_box = None
        self.search_filter = ""

    def handle_animation_change(
        self, property_name: TAnimatedProperty, _instance, value: float
    ):
        match property_name:
            case "size_hint_x_closed":
                self.size_hint_x = value
                self.drawer_close_animation = Animation(
                    size_hint_x=value,
                    duration=self.animation_open_duration,
                    t=self.animation_open_timing,
                )
                self.drawer_close_animation.bind(
                    on_complete=lambda *_: setattr(self, "open_state", OpenState.closed)
                )
            case "size_hint_x_open":
                self.drawer_open_animation = Animation(
                    size_hint_x=value,
                    duration=self.animation_open_duration,
                    t=self.animation_open_timing,
                )
                self.drawer_open_animation.bind(
                    on_complete=lambda *_: setattr(self, "open_state", OpenState.open)
                )
            case "animation_open_duration":
                self.drawer_open_animation = Animation(
                    size_hint_x=self.size_hint_x_open,
                    duration=value,
                    t=self.animation_open_timing,
                )
                self.fade_in_animation = Animation(
                    opacity=1,
                    duration=value,
                    t=self.animation_open_timing,
                )
            case "animation_open_timing":
                self.drawer_open_animation = Animation(
                    size_hint_x=self.size_hint_x_open,
                    duration=self.animation_open_duration,
                    t=value,
                )
                self.fade_in_animation = Animation(
                    opacity=1,
                    duration=self.animation_open_duration,
                    t=value,
                )
            case "animation_closed_duration":
                self.drawer_close_animation = Animation(
                    size_hint_x=self.size_hint_x_closed,
                    duration=value,
                    t=self.animation_closed_timing,
                )
                self.fade_out_animation = Animation(
                    opacity=0,
                    duration=value,
                    t=self.animation_closed_timing,
                )
            case "animation_closed_timing":
                self.drawer_close_animation = Animation(
                    size_hint_x=self.size_hint_x_closed,
                    duration=self.animation_closed_duration,
                    t=value,
                )
                self.fade_out_animation = Animation(
                    opacity=0,
                    duration=self.animation_closed_duration,
                    t=value,
                )
            case _:
                Logger.warning(f"Unknown property: {property_name}")
                raise ValueError(f"Unknown property: {property_name}")

    def on_open_state(self, _instance, _value: TOpenState | OpenState):
        match _value:
            case OpenState.open:
                self.dispatch("on_open", _instance, _value)
            case OpenState.closed:
                self.dispatch("on_close", _instance, _value)
            case OpenState.opening:
                self.dispatch("on_opening", _instance, _value)
            case OpenState.closing:
                self.dispatch("on_closing", _instance, _value)
            case _:
                msg = f"Invalid state: {_value}"
                raise ValueError(msg)

    def on_open(self, _instance, _value):
        self.open_state = OpenState.open
        self.fade_in_animation.start(self.clear_search_button)
        self.fade_in_animation.start(self.search_box)

    def on_opening(self, _instance, _value):
        self.drawer_close_animation.cancel(self)
        self.fade_out_animation.cancel(self.ids.nav_items)
        self.ids.menu_button.pos_hint = self._menu_button_pos_hint_open
        self.attach_search_box()

        self.fade_out_animation.cancel(self.clear_search_button)
        self.fade_out_animation.start(self.search_box)
        self.fade_in_animation.start(self.ids.nav_items)
        self.drawer_open_animation.start(self)

    def on_closing(self, _instance, _value):
        self.fade_in_animation.cancel(self.ids.nav_items)
        self.drawer_open_animation.cancel(self)
        self.fade_in_animation.cancel(self.clear_search_button)
        self.fade_in_animation.cancel(self.search_box)
        self.fade_out_animation.start(self.clear_search_button)
        self.fade_out_animation.start(self.search_box)
        self.fade_out_animation.start(self.ids.nav_items)
        self.drawer_close_animation.start(self)

    def on_close(self, _instance, _value):
        self.open_state = OpenState.closed
        self.ids.menu_button.pos_hint = self._menu_button_pos_hint_closed
        self.detach_search_box()

    def toggle(self, _instance: ThemedIconButton | None):
        match self.open_state:
            case OpenState.open:
                self.on_open_state(self, OpenState.closing)
            case OpenState.closed:
                self.on_open_state(self, OpenState.opening)
            case OpenState.opening:
                self.on_open_state(self, OpenState.closing)
            case OpenState.closing:
                self.on_open_state(self, OpenState.opening)

    def handle_nav_selected(self, instance: "NavItem") -> bool:
        """Before bubbling up, check that the drawer is open"""
        if self.open_state == OpenState.closed:
            return True
        if self.nav_id_selected == instance.nav_id:
            return True
        Clock.schedule_once(self.update_nav_selection, 0)
        if self.close_on_nav and self.open_state in (OpenState.open, OpenState.opening):
            self.toggle(None)

        return self.dispatch("on_nav_selected", instance)

    def on_nav_selected(self, _instance: "NavItem"):
        return True

    def on_search_clear(self, _instance: ThemedIconButton | None):
        if self.search_box is not None:
            self.search_filter = ""
            self.search_box.text = ""
            self.search_box.focus = False

        return True

    def on_search_filter(self, _instance, value: str):
        """We maintain the state of search filter but debounce our dispatches - unless its cleared"""

        if self._search_filter_sch_event is not None:
            Clock.unschedule(self._search_filter_sch_event)
            self._search_filter_sch_event = None
        self._search_filter_sch_event = Clock.schedule_once(
            partial(self._dispatch_search_filter, value=value.lower()),
            timeout=0.1 if value else 0,
        )

    def _dispatch_search_filter(self, _dt, value: str):
        self._search_filter_sch_event = None
        self.render_nav_items()

    def update_nav_selection(self, _dt):
        for widget in self.ids.nav_items.main_children():
            widget.selected = self.nav_id_selected == widget.nav_id

    def add_widget_to_drawer(self, widget: "NavItem"):
        widget.bind(on_release=lambda _: self.handle_nav_selected(widget))
        self.ids.nav_items.add_widget_to_main(widget)

    def clear_widgets_from_drawer(self):
        self.ids.nav_items.clear_widgets_from_main()

    def render_nav_items(self, *_args):
        """On a change, re-render all the nav items"""
        self.ids.nav_items.clear_widgets_from_main()
        items: list[NavItemData] = self.nav_data_items[:]
        needle: str = self.search_filter.lower()
        displayed_items = (
            items
            if not needle
            else list(filter(lambda i: needle in i.text.lower(), items))
        )
        for item in displayed_items:
            widget = NavItem(text=item.text, nav_id=item.nav_id, selected=item.selected)
            self.add_widget_to_drawer(widget)

    def on_nav_data_items(self, _widget, value):
        self.render_nav_items()
