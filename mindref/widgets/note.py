from typing import TYPE_CHECKING

from kivy import Logger
from kivy.app import App
from kivy.cache import Cache
from kivy.properties import (
    DictProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from domain.events import (
    AddNoteEvent,
    BackButtonEvent,
    EditNoteEvent,
    ListViewButtonEvent,
    PaginationEvent,
)

from utils import import_kv
from utils.caching import cache_key_note, kivy_cache
from widgets.behavior.gesture_rec_behavior import GestureRecognizingBehavior
from widgets.markdown.markdown_document import MarkdownDocument

import_kv(__file__)


if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNoteDict
    from typing import Optional
    from domain.protocols import AppRegistryProtocol

Cache.register("note_widget", limit=10, timeout=3600)


# noinspection PyUnusedLocal
@kivy_cache(cache_name="note_widget", key_func=cache_key_note)
def get_cached_note(*, content_data: "MarkdownNoteDict", parent: "NoteContent"):
    return MarkdownDocument(content_data=content_data)


class Note(BoxLayout, GestureRecognizingBehavior):
    note_title = StringProperty()
    note_index = NumericProperty()
    note_content = DictProperty()
    note_control = ObjectProperty()

    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)
        self.bind(on_swipe=self.handle_swipe)

    def handle_swipe(self, _instance, _score, gesture):
        app = App.get_running_app()
        if gesture.name == "swipe-left":
            app.registry.push_event(PaginationEvent(direction=-1))
        elif gesture.name == "swipe-right":
            app.registry.push_event(PaginationEvent(direction=1))
        return True

    def set_note_content(self, note_data: "Optional[MarkdownNoteDict]"):
        self.note_title = note_data.get("title", "")
        self.note_index = note_data.get("idx", -1)
        self.note_content = note_data if note_data else {}


class NoteContent(BoxLayout):
    content = DictProperty()

    def __init__(self, **kwargs):
        super(NoteContent, self).__init__(**kwargs)
        self.bind(content=self.handle_content)

    def handle_content(self, _, content_data: "MarkdownNoteDict"):
        self.clear_widgets()
        self._set_markdown(content_data)

    def _set_markdown(self, content_data: "MarkdownNoteDict"):
        md_widget = get_cached_note(content_data=content_data, parent=self)
        self.add_widget(md_widget)


class NoteTitleBar(BoxLayout):
    title = StringProperty()
    index = NumericProperty()
    action_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(action_button=self.handle_button_bind)

    def handle_button_bind(self, *_args):
        self.action_button.bind(on_select=self.handle_select)

    def handle_select(self, _, value):

        app: "AppRegistryProtocol" = App.get_running_app()
        match value:
            case "add":
                event = AddNoteEvent()
                app.registry.push_event(event)
                Logger.info(
                    f"{type(self).__name__}: handle_select : 'add',  pushed:{event!r}"
                )
                return True
            case "edit":
                event = EditNoteEvent(category=app.note_category, idx=self.index)
                app.registry.push_event(event)
                Logger.info(
                    f"{type(self).__name__}: handle_select : 'edit', pushed: {event!r}"
                )
                return True
            case "list":
                event = ListViewButtonEvent()
                app.registry.push_event(event)
                Logger.info(
                    f"{type(self).__name__}: handle_select : 'list', pushed: {event!r}"
                )
                return True
            case "back":
                event = BackButtonEvent(display_state=app.display_state)
                app.registry.push_event(
                    BackButtonEvent(display_state=app.display_state)
                )
                Logger.info(
                    f"{type(self).__name__}: handle_select : 'back', pushed: {event!r}"
                )
                return True
            case _:
                Logger.warning(
                    f"{type(self).__name__}: handle_select - Unhandled value {value}"
                )
