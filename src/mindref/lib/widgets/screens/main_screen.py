from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from mindref.lib import get_app
from mindref.lib.domain.events import RefreshNotesEvent
from mindref.lib.widgets.nav_drawer import NavItem

if TYPE_CHECKING:
    from mindref.lib.widgets.nav_drawer import NavDrawer
    from mindref.lib.widgets.refreshable import V2RefreshContainer


Builder.load_string(
    """
#:import V2RefreshContainer mindref.lib.widgets.refreshable.refresh_container
#:import ScrollingListView mindref.lib.widgets.list_view.list_view
#:import OpenMenuButton mindref.lib.widgets.buttons
#:import NavDrawer mindref.lib.widgets.nav_drawer
#:import OpenMenuButton mindref.lib.widgets.buttons
#:import AnimatedHSeparator mindref.lib.widgets.separator

    
<MainScreen>:
    app: app
    canvas:
        Color:
            rgba: app.colors['Gray-900']
        Rectangle:
            size: self.size
            pos: self.pos
    RelativeLayout:
        V2RefreshContainer:
            id: scroller
            size_hint_y: 1
            pos_hint: {"x": 0.1, "y": 0}
        NavDrawer:
            id: nav_drawer
            size_hint_x_closed: 0.07
            size_hint_x_open: 0.5
            nav_link_padding: [0, dp(16), 0, dp(16)]
            nav_id_selected: root.selected_note
            canvas.before:
                Color:
                    rgba: app.colors['Dark']
                Rectangle:
                    size: self.size
                    pos: self.pos        
        
"""
)


class V2NoteListViewScreenIds(NamedTuple):
    scroller: "V2RefreshContainer"
    nav_drawer: "NavDrawer"


class MainScreen(Screen):
    app = ObjectProperty()
    ids: V2NoteListViewScreenIds
    selected_note = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._bind_scroller, 0)
        Clock.schedule_once(self._bind_nav_drawer, 0)
        self.app = get_app()
        self.app.bind(note_files=self.handle_note_files)

    def _bind_scroller(self, _dt):
        scroller = self.ids.scroller
        scroller.fbind("on_refresh", self.on_refresh)

    def _bind_nav_drawer(self, _dt):
        nav_drawer = self.ids.nav_drawer
        Logger.info(f"{type(self).__name__} : {nav_drawer=}")
        nav_drawer.fbind("on_nav_selected", self.handle_nav_click)

    def on_refresh(self, *args):
        Logger.info(f"{type(self).__name__} : on_refresh called")

        def on_complete(_dt: float):
            Logger.info(f"{type(self).__name__} : Refresh completed {_dt=}")
            self.ids.scroller.refreshing = False

        self.app.registry.push_event(RefreshNotesEvent(on_complete))

    def handle_nav_click(self, _dt, instance: "NavItem"):
        nav_id = instance.nav_id
        self.selected_note = nav_id if not instance.selected else None

    def handle_note_files(self, _, value: list[Path]):
        nav_drawer = self.ids.nav_drawer
        nav_drawer.clear_widgets_from_drawer()
        for note in value:
            button = NavItem(
                text=str(note.stem),
                nav_id=str(note.stem),
                selected=self.selected_note == str(note.stem),
            )

            nav_drawer.add_widget_to_drawer(button)
