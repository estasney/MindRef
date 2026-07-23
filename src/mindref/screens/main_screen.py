from typing import TYPE_CHECKING, NamedTuple

import mistune  # type: ignore
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
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


<MainScreen>:
    app: app
    note_files: app.note_files
    top_strip_height: menu_button.height
    canvas:
        Color:
            rgba: app.colors['Gray-900']
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: app.colors['Dark']
        Rectangle:
            size: (self.width, self.top_strip_height)
            pos: (self.x, self.top - self.top_strip_height)
    RelativeLayout:
        ScrollView:
            id: content
            size_hint: 1, None
            height: root.height - menu_button.height
            pos_hint: {"x": 0, "y": 0}
        NavDrawer:
            id: nav_drawer
            size_hint_x: 0.8 if root.height > root.width else 0.5
            top_bar_left_inset: menu_button.width
            top_bar_height: menu_button.height
            nav_link_padding: [0, dp(16), 0, dp(16)]
            nav_id_selected: root.selected_note
            open_state: 'closed'
            canvas.before:
                Color:
                    rgba: app.colors['Dark']
                Rectangle:
                    size: self.size
                    pos: self.pos
        OpenMenuButton:
            id: menu_button
            size_hint: None, None
            width: self.height
            pos_hint: {"top": 1}
            x: dp(4)
            on_release: nav_drawer.toggle(self)

"""
)


class V2NoteListViewScreenIds(NamedTuple):
    content: "ScrollView"
    nav_drawer: "NavDrawer"


class MainScreen(Screen, V2RefreshBehavior):
    app = ObjectProperty()
    ids: V2NoteListViewScreenIds
    selected_note = StringProperty(None, allownone=True)
    top_strip_height = NumericProperty(0)
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
            self.app.refresh_note_files()
            return True
        return super().on_refresh(widget, state, to_children)

    def on_selected_note(self, _instance, note_id: str | None) -> bool:
        if not note_id:
            self.ids.content.clear_widgets()
            return True
        note_content = self.app.read_note(note_id)
        Clock.schedule_once(lambda _: self.render_note(note_content), 0)
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

    def render_note(self, note_text: str):
        """Read a markdown file, parse it, and render it in the scroller."""

        self.ids.content.clear_widgets()
        document_md = self._markdown_parser(note_text)
        layout = MarkdownDocumentLayout()
        layout.padding = [dp(16), 0, dp(16), 0]
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
