from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, Optional

import mistune
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from mindref.lib import get_app
from mindref.lib.domain.events import RefreshNotesEvent
from mindref.lib.domain.parser.kbd_plugin import plugin_kbd
from mindref.lib.widgets.markdown.markdown_document import MarkdownDocument
from mindref.lib.widgets.nav_drawer import NavItem

if TYPE_CHECKING:
    from mindref.lib.domain.markdown_note import MarkdownNoteDict
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
    _markdown_parser = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._bind_scroller, 0)
        Clock.schedule_once(self._bind_nav_drawer, 0)
        self.app = get_app()
        self.app.bind(note_files=self.handle_note_files)
        # Initialize the markdown parser
        self._markdown_parser = mistune.create_markdown(
            escape=False, renderer=mistune.AstRenderer(), plugins=["table", plugin_kbd]
        )

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

        if self.selected_note:
            # Find the note file path
            note_path = self._find_note_path(self.selected_note)
            if note_path:
                # Read and render the note
                self.read_and_render_note(note_path)
        else:
            # Clear the scroller when no note is selected
            self.ids.scroller.clear_widgets_from_main()

    def _find_note_path(self, note_name: str) -> Optional[Path]:
        """Find the path to a note file by its name."""
        for note_path in self.app.note_files:
            if note_path.stem == note_name:
                return note_path
        return None

    def read_and_render_note(self, note_path: Path):
        """Read a markdown file, parse it, and render it in the scroller."""
        try:
            # Clear the scroller
            self.ids.scroller.clear_widgets_from_main()

            # Read the file content
            text = note_path.read_text(encoding="utf-8")

            # Parse the markdown
            document = self._markdown_parser(text)

            # Extract title from the first heading or use the filename
            title = note_path.stem
            for node in document:
                if node["type"] == "heading" and node.get("level", 0) == 1:
                    if node.get("children") and node["children"][0].get("text"):
                        title = node["children"][0]["text"]
                        # Remove the title node from the document
                        document = [n for n in document if n != node]
                        break

            # Create a content dictionary
            content_data = {"document": document, "text": text, "title": title}

            # Create and add the markdown document widget
            md_widget = MarkdownDocument(content_data=content_data)
            self.ids.scroller.add_widget_to_main(md_widget)

            Logger.info(f"{type(self).__name__} : Rendered note {note_path.name}")
        except Exception as e:
            Logger.error(f"{type(self).__name__} : Error rendering note: {e}")

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
