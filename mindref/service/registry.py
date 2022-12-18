from collections import deque
from pathlib import Path
from typing import Callable, Optional, TYPE_CHECKING

from kivy import Logger

from domain.events import (
    NoteCategoryEvent,
    NoteCategoryFailureEvent,
    NoteFetchedEvent,
    NotesQueryNotSetFailureEvent,
    FilePickerEvent,
)
from utils import caller, def_cb, sch_cb
from utils.caching import kivy_cache
from widgets.typeahead.typeahead_dropdown import Suggestion

if TYPE_CHECKING:
    from domain.protocols import AppRegistryProtocol
    from domain.markdown_note import MarkdownNote, MarkdownNoteDict
    from domain.events import Event
    from domain.editable import EditableNote


class Registry:
    """Orchestration"""

    _app: Optional["AppRegistryProtocol"]
    events: deque["Event"]

    def __init__(self):
        super().__init__()
        self._app = None
        self.events = deque([])

    @property
    def app(self):
        if self._app is None:
            raise AttributeError(f"Registry has no App")
        return self._app

    @app.setter
    def app(self, app: "AppRegistryProtocol"):
        self._app = app

    def set_note_storage_path(self, path: Path | str):
        self.app.note_service.storage_path = path
        Logger.info(f"{type(self).__name__}: Set Note Service Storage Path - {path!s}")

    def push_event(self, event: "Event"):
        self.events.append(event)

    def paginate_note(self, direction: int):
        """
        Increment our index, show a note transition and update app.note_data

        Then we emit an on_paginate event

        Parameters
        ----------
        direction

        Returns
        -------
        """

        def after_note_fetched(note: "MarkdownNote"):
            """Callback from note_service"""
            note_data = note.to_dict()
            Logger.info(
                f"{type(self).__name__}: after_note_fetched - Set App Note Data to {note!r}"
            )
            trigger_pause_state = caller(self.app, "play_state_trigger", "pause")
            trigger_display = caller(self.app, "display_state_trigger", "display")
            emit_paginate = caller(
                self.app, "dispatch", "on_paginate", (direction, note_data)
            )
            sch_cb(trigger_pause_state, trigger_display, emit_paginate, timeout=0.1)

        match direction:
            case 0:
                return self.set_note_index(self.app.note_service.index.current)
            case 1:
                fetch_note = caller(
                    self.app.note_service,
                    "get_next_note",
                    on_complete=after_note_fetched,
                )
                sch_cb(fetch_note)
                Logger.info(f"{type(self).__name__}: paginate_note - forwards")
            case -1:
                fetch_note = caller(
                    self.app.note_service,
                    "get_previous_note",
                    on_complete=after_note_fetched,
                )
                sch_cb(fetch_note)
                Logger.info(f"{type(self).__name__}: paginate_note - backwards")
            case _:
                raise NotImplementedError(f"Pagination of {direction} not supported")

    def set_note_index(self, value: int):

        """
        Manually set note_index and orchestrate backend

        Parameters
        ----------
        value : int
            The note index

        Notes
        -------
        - Clear Note Data
        - Call App.note_service.set_index
        - Get Note Data
        - Set It
        """

        set_note_index = caller(self.app.note_service, "set_index", value)

        def after_note_fetched(note: "MarkdownNote"):
            """Callback from note_service"""
            note_data = note.to_dict()
            Logger.info(
                f"{type(self).__name__}: after_note_fetched - "
                f"Set App Note Data to {note!r}"
            )
            trigger_pause_state = caller(self.app, "play_state_trigger", "pause")
            trigger_display = caller(self.app, "display_state_trigger", "display")
            emit_paginate = caller(self.app, "dispatch", "on_paginate", (0, note_data))
            sch_cb(trigger_pause_state, trigger_display, emit_paginate, timeout=0.1)

        fetch_note = caller(
            self.app.note_service, "get_current_note", on_complete=after_note_fetched
        )
        sch_cb(set_note_index, fetch_note)
        Logger.info(f"{type(self).__name__}: set_note_index - {value}")

    def set_note_category(self, value: Optional[str], on_complete: Optional[Callable]):
        """
        Update note_service current category.

        If Exception occurs (KeyError) push an error event

        Notes
        ------
        App will update it's own note_category in `App.process_note_category_event`
        """
        try:
            self.app.note_service.current_category = value
        except KeyError:
            self.app.note_service.current_category = None
            self.push_event(
                NoteCategoryFailureEvent(on_complete=on_complete, value=value)
            )
            return
        self.push_event(NoteCategoryEvent(on_complete=on_complete, value=value))

    def query_category(
        self,
        category: str,
        query: str,
        on_complete: Callable[[Optional[list[Suggestion]]], None],
    ):
        """
        String search for a category
        """
        note_repo = self.app.note_service
        if not note_repo.configured:
            self.push_event(NotesQueryNotSetFailureEvent(on_complete=on_complete))
            return
        result = note_repo.query_notes(category=category, query=query, on_complete=None)
        on_complete(result)

    def query_all(self, on_complete: Optional[Callable] = None):
        """
        Returns immediately after invoking note_repo.discover_notes

        note_repo.discover_notes will push a NotesDiscoveryEvent with results
        """
        self.app.screen_manager.dispatch("on_refresh", True)
        Logger.debug(f"{type(self).__name__}: query_all - Dispatched 'on_refresh'")
        note_repo = self.app.note_service
        if not note_repo.configured:
            e = NotesQueryNotSetFailureEvent(on_complete=on_complete)
            self.push_event(NotesQueryNotSetFailureEvent(on_complete=on_complete))
            Logger.info(
                f"{type(self).__name__}: query_all - app.note_service not configured. Pushed {e!r}"
            )
            return

        clear_refresh = caller(self.app.screen_manager, "dispatch", "on_refresh", False)
        if on_complete:
            chained_complete = def_cb(on_complete, clear_refresh)
        else:
            chained_complete = clear_refresh
        note_repo.discover_categories(chained_complete)

    def clear_caches(self):
        from kivy.cache import Cache

        categories_seen = getattr(kivy_cache, "categories_seen")
        for category in categories_seen:
            Cache.remove(category, key=None)

    def clear_cache(self, category, key=None):
        from kivy.cache import Cache

        Cache.remove(category, key)

    def new_note(self, category: Optional[str], idx: Optional[int]) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index_size() + 1
        note = self.app.editor_service.new_note(category=category, idx=idx)
        return note

    def edit_note(self, category: Optional[str], idx: Optional[int]) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index.current
        md_note = self.app.note_service.get_note(
            category=category, idx=idx, on_complete=None
        )
        data_note = self.app.editor_service.edit_note(md_note)
        return data_note

    def save_note(self, note: "EditableNote"):
        """
        We need to persist the note, and either add or modify its data in category metadata

        - Store Note To Disk
        - Add or Replace Note Data
        - Add or Replace Note Metadata
        - Change App display state to 'display'
        """

        def update_app_meta(meta: list["MarkdownNoteDict"]):
            self.app.note_category_meta = meta

        def push_fetched_event(md_note: "MarkdownNote"):
            Logger.info(f"{type(self).__name__} : Note Service says note was saved")
            self.clear_cache("category_meta")
            self.clear_cache("note_widget")
            self.push_event(NoteFetchedEvent(note=md_note))
            # We can leave refresh as False, the note was refreshed by note service
            self.app.note_service.get_category_meta(
                self.app.note_category, on_complete=update_app_meta, refresh=False
            )

        # store note to disk
        self.app.note_service.save_note(note, on_complete=push_fetched_event)
        Logger.info(f"{type(self).__name__}: save_note - {note!r}")

    def handle_picker_event(self, event: FilePickerEvent):
        e = FilePickerEvent.Action
        Logger.info(f"{type(self).__name__}: handle_picker_event - {event}")
        app = self.app
        match event, app.platform_android:
            case FilePickerEvent(action=e.OPEN_FOLDER), True:
                # Note Service
                return app.note_service.prompt_for_external_folder(
                    on_complete=event.on_complete
                )
            case FilePickerEvent(action=e.OPEN_FILE), True:
                raise NotImplementedError()
            case FilePickerEvent(
                action=e.OPEN_FOLDER | e.OPEN_FILE, start_folder=str()
            ), False:
                return app.screen_manager.open_file_picker(event)
            case FilePickerEvent(
                action=e.OPEN_FOLDER | e.OPEN_FILE, start_folder=None
            ), False:
                event = FilePickerEvent(
                    on_complete=event.on_complete,
                    action=event.action,
                    start_folder=str(app.note_service.storage_path),
                    ext_filter=event.ext_filter,
                )
                return app.screen_manager.open_file_picker(event)

            case FilePickerEvent(action=e.CLOSE), False:
                raise NotImplementedError()
