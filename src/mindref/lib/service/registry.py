from collections import deque
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

from kivy import Logger

from mindref.lib.domain.events import (
    EventFailure,
    FilePickerEvent,
    NoteCategoryEvent,
    NoteCategoryFailureEvent,
    NoteFetchedEvent,
    NotesQueryErrorFailureEvent,
    NotesQueryFailureEvent,
    NotesQueryNotSetFailureEvent,
)
from mindref.lib.utils import def_cb, sch_cb, schedulable
from mindref.lib.utils.caching import kivy_cache

if TYPE_CHECKING:
    from mindref.lib.domain.editable import EditableNote
    from mindref.lib.domain.events import Event
    from mindref.lib.domain.markdown_note import MarkdownNote, MarkdownNoteDict
    from mindref.lib.domain.protocols import AppRegistryProtocol
    from mindref.lib.widgets.typeahead.typeahead_dropdown import Suggestion


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
            raise AttributeError("Registry has no App")
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

            trigger_display = schedulable(self.app.display_state_trigger, "display")
            emit_paginate = schedulable(
                self.app.dispatch, "on_paginate", (direction, note_data)
            )
            sch_cb(trigger_display, emit_paginate, timeout=0.1)

        match direction:
            case 0:
                return self.set_note_index(self.app.note_service.index.current)
            case 1:
                fetch_note = schedulable(
                    self.app.note_service.get_next_note, on_complete=after_note_fetched
                )
                sch_cb(fetch_note)
                Logger.info(f"{type(self).__name__}: paginate_note - forwards")
                return None
            case -1:
                fetch_note = schedulable(
                    self.app.note_service.get_previous_note,
                    on_complete=after_note_fetched,
                )
                sch_cb(fetch_note)
                Logger.info(f"{type(self).__name__}: paginate_note - backwards")
                return None
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

        set_note_index = schedulable(self.app.note_service.set_index, value)

        def after_note_fetched(note: "MarkdownNote"):
            """Callback from note_service"""
            note_data = note.to_dict()
            Logger.info(
                f"{type(self).__name__}: after_note_fetched - "
                f"Set App Note Data to {note!r}"
            )

            trigger_display = schedulable(self.app.display_state_trigger, "display")
            emit_paginate = schedulable(
                self.app.dispatch, "on_paginate", (0, note_data)
            )
            sch_cb(trigger_display, emit_paginate, timeout=0.1)

        fetch_note = schedulable(
            self.app.note_service.get_current_note, on_complete=after_note_fetched
        )
        sch_cb(set_note_index, fetch_note)
        Logger.info(f"{type(self).__name__}: set_note_index - {value}")

    def set_note_category(self, value: str | None, on_complete: Callable | None):
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
        on_complete: Callable[[list["Suggestion"] | None], None],
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

    def query_all(self, on_complete: Callable | None = None):
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

        clear_refresh = schedulable(
            self.app.screen_manager.dispatch, "on_refresh", False
        )
        if on_complete:
            chained_complete = def_cb(on_complete, clear_refresh)
        else:
            chained_complete = clear_refresh
        note_repo.discover_categories(chained_complete)

    def clear_caches(self):
        from kivy.cache import Cache

        categories_seen = getattr(kivy_cache, "categories_seen", [])
        for category in categories_seen:
            Cache.remove(category, key=None)

    def clear_cache(self, category, key=None):
        from kivy.cache import Cache

        Cache.remove(category, key)

    def new_note(self, category: str | None, idx: int | None) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index_size() + 1
        return self.app.editor_service.new_note(category=category, idx=idx)

    def edit_note(self, category: str | None, idx: int | None) -> "EditableNote":
        category = category if category else self.app.note_category
        idx = idx if idx is not None else self.app.note_service.index.current
        md_note = self.app.note_service.get_note(
            category=category, idx=idx, on_complete=None
        )
        return self.app.editor_service.edit_note(md_note)

    def save_note(self, note: "EditableNote"):
        """
        We need to persist the note, and either add or modify its data in category metadata

        - Store Note To Disk
        - Add or Replace Note Data
        - Add or Replace Note Metadata
        - Change App display state to 'display'
        - Clear Editor
        """

        def update_app_meta(meta: list["MarkdownNoteDict"]) -> None:
            self.app.note_category_meta = meta

        def push_fetched_event(md_note: "MarkdownNote") -> None:
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
                return app.note_service.prompt_for_external_file(
                    ext_filter=event.ext_filter, on_complete=event.on_complete
                )
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
                raise NotImplementedError

    def create_category(
        self,
        category: str,
        image_path: str | Path,
        on_complete: Callable[[Path, bool], None],
    ):
        """
        Create a new category

        Parameters
        ----------
        category : str
            The name of the category to create
        image_path : str | Path
            The path to the image to use for the category
        on_complete : Callable[[Path, bool], None]
            Dual purpose callback. First argument is the category name, second is a boolean indicating success.


        """
        note_repo = self.app.note_service
        if not note_repo.configured:
            self.push_event(NotesQueryNotSetFailureEvent(on_complete=None))
            return
        note_repo.create_category(category, image_path, on_complete=on_complete)

    def handle_error(self, event: EventFailure):
        """
        Handle an error event
        """
        match event:
            case NotesQueryFailureEvent():
                ...
            case NotesQueryNotSetFailureEvent():
                ...
            case NotesQueryErrorFailureEvent():
                ...
            case EventFailure():
                ...

    def handle_category_validation(
        self, field: Literal["name", "image"], value: str
    ) -> str | None:
        """
        Validate the category name or image path provided by the user in the category editor

        Parameters
        ----------
        field : Literal['name', 'image']
            The field name to validate
        value : str
            The value to validate

        Returns
        -------
        None if valid, otherwise a string describing the error

        Notes
        -----
        - Category names must be unique, this includes by case. NoteService will determine if
          the name is unique by case-insensitive comparison of known category (folder) names.
            - Leading and trailing whitespace is stripped from the name, so '  My Category  ' is
              the same as 'My Category'
        - Category image paths have different requirements depending on the platform
           - Desktop: Must be a valid path to an existing file, and the file extension must be one of the following:
                - .png
                - .jpg
                - .jpeg
           - Android: The image path must not be empty. As is, we don't have a way to validate the path, nor do we have
               a way to validate the file extension. As such, we'll just assume the user knows what they're doing.
        """

        match field:
            case "name":
                if not value:
                    return "Category name cannot be empty"
                if not self.app.note_service.category_name_unique(value):
                    return "Category name must be unique"
                return None

            case "image" if self.app.platform_android:
                if not value:
                    return "Category image cannot be empty"
                return None

            case "image":
                if not value:
                    return "Category image cannot be empty"
                if not Path(value).exists():
                    return "Category image must be a valid path to an existing file"
                if Path(value).suffix.lower() not in (".png", ".jpg", ".jpeg"):
                    return "Category image must be a .png, .jpg, or .jpeg file"
                return None
