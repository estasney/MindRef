from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import mistune  # type: ignore
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from mindref.app_notes import NoteFile
from mindref.lib import get_app
from mindref.lib.domain.parser.kbd_plugin import plugin_kbd
from mindref.lib.widgets.markdown.markdown_document_v2 import MarkdownDocumentLayout
from mindref.lib.widgets.refreshable import V2RefreshBehavior

if TYPE_CHECKING:
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.widget import Widget

    from mindref.lib.widgets.nav_drawer import NavDrawer, NavItem

Builder.load_string(
    """
#:import V2RefreshContainer mindref.lib.widgets.refreshable.refresh_container
#:import ScrollingListView mindref.lib.widgets.list_view.list_view
#:import NavDrawer mindref.lib.widgets.nav_drawer
#:import OpenMenuButton mindref.lib.widgets.buttons
#:import AnimatedHSeparator mindref.lib.widgets.separator
#:import Note mindref.lib.widgets.note.Note

<MainScreen>:
    app: app
    note_files: app.note_files
    canvas:
        Color:
            rgba: app.colors['Gray-900']
        Rectangle:
            size: self.size
            pos: self.pos
    RelativeLayout:
        ScrollView:
            id: content
            size_hint_y: 1
            size_hint_x: 0.93
            pos_hint: {"x": 0.09, "y": 0}
        NavDrawer:
            id: nav_drawer
            size_hint_x_closed: 0.07
            size_hint_x_open: 0.5
            nav_link_padding: [0, dp(16), 0, dp(16)]
            nav_id_selected: root.selected_note
            open_state: 'opening'
            canvas.before:
                Color:
                    rgba: app.colors['Dark']
                Rectangle:
                    size: self.size
                    pos: self.pos        

"""
)


class V2NoteListViewScreenIds(NamedTuple):
    content: "ScrollView"
    nav_drawer: "NavDrawer"


class MainScreen(Screen, V2RefreshBehavior):
    app = ObjectProperty()
    ids: V2NoteListViewScreenIds
    selected_note = StringProperty(None, allownone=True)
    _markdown_parser: mistune.Markdown

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._bind_nav_drawer, 0)
        self.app = get_app()
        self.app.bind(note_files=self.handle_note_files)
        self._markdown_parser = mistune.create_markdown(
            escape=False, renderer=mistune.AstRenderer(), plugins=["table", plugin_kbd]
        )

    def _bind_nav_drawer(self, _dt):
        nav_drawer = self.ids.nav_drawer
        nav_drawer.fbind("on_nav_selected", self.handle_nav_click)

    def on_refresh(self, widget: "Widget", state: bool, to_children: bool) -> bool:
        if not to_children:
            self.selected_note = None
            self.app.registry.query_all_v2()
            return True
        return super().on_refresh(widget, state, to_children)

    def on_selected_note(self, _instance, value: str | None) -> bool:
        if not value:
            self.ids.content.clear_widgets()
            return True
        note_path = self._find_note_file(value)
        if note_path:
            self.read_and_render_note(note_path)
            return True
        Logger.error(f"{type(self).__name__} : Note file not found for ID {value}")
        self.ids.content.clear_widgets()
        return True

    def handle_nav_click(self, _dt, instance: "NavItem"):
        nav_id = instance.nav_id
        self.selected_note = nav_id if not instance.selected else None

        return True

    def _find_note_file(self, note_id: str) -> NoteFile | None:
        return next(
            (note_path for note_path in self.app.note_files if note_path.id == note_id),
            None,
        )

    def read_and_render_note(self, note_file: NoteFile):
        """Read a markdown file, parse it, and render it in the scroller."""

        self.ids.content.clear_widgets()
        text = note_file.read_text()
        document_md = self._markdown_parser(text)
        layout = MarkdownDocumentLayout()
        layout.padding = [0, 0, dp(32), 0]
        self.ids.content.add_widget(layout)
        layout.document = document_md

    def handle_note_files(self, _, value: list[NoteFile]):
        Logger.info(
            f"{type(self).__name__} : handle_note_files - {len(value)} note files found."
        )
        self.selected_note = None
        from mindref.lib.widgets.nav_drawer.nav_item import NavItemData

        nav_data_items = [
            NavItemData.from_note_file(note, selected=self.selected_note == note.id)
            for note in value
        ]
        self.ids.nav_drawer.nav_data_items = nav_data_items
