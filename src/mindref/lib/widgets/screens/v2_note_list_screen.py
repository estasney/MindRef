from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from mindref.lib import get_app
from mindref.lib.domain.events import RefreshNotesEvent

if TYPE_CHECKING:
    from mindref.lib.widgets.refreshable import V2RefreshContainer


Builder.load_string(
    """
#:import V2RefreshContainer mindref.lib.widgets.refreshable.refresh_container
#:import ScrollingListView mindref.lib.widgets.list_view.list_view
#:import OpenMenuButton mindref.lib.widgets.buttons
#:import NavDrawer mindref.lib.widgets.nav_drawer
#:import OpenMenuButton mindref.lib.widgets.buttons
#:import AnimatedHSeparator mindref.lib.widgets.separator

    
<V2NoteListViewScreen>:
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


class V2NoteListViewScreen(Screen):
    app = ObjectProperty()
    ids: V2NoteListViewScreenIds

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self._bind_scroller, 0)
        self.app = get_app()
        self.app.bind(note_files=self.handle_note_files)

    def _bind_scroller(self, _dt):
        scroller = self.ids.scroller
        scroller.fbind("on_refresh", self.on_refresh)

    def on_refresh(self, *args):
        Logger.info(f"{type(self).__name__} : on_refresh called")

        def on_complete(_dt: float):
            Logger.info(f"{type(self).__name__} : Refresh completed {_dt=}")
            self.ids.scroller.refreshing = False

        self.app.registry.push_event(RefreshNotesEvent(on_complete))

    def handle_note_files(self, _, value: list[Path]):
        Logger.info(f"{type(self).__name__} : handle_note_files {value}")
        layout = self.ids.scroller
        layout.clear_widgets_from_grid()
        for note in value:
            layout.add_widget_to_grid(
                Label(text=str(note.stem), size_hint_y=None, height=40)
            )
        nav_layout = self.ids.nav_drawer
        nav_layout.clear_widgets_from_drawer()
        for note in value:
            nav_layout.add_widget_to_drawer(
                Label(text=str(note.stem), size_hint_y=None, height=40)
            )
