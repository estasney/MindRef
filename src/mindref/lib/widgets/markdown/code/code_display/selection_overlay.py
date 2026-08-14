from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget

from mindref.app_theme import THEME_COLORS
from mindref.lib.widgets.flash_pill import FlashPill
from mindref.lib.widgets.markdown.code.code_display.enums import HandleRole
from mindref.lib.widgets.markdown.code.code_display.selection_drag_handle import (
    SelectionDragHandle,
)
from mindref.lib.widgets.markdown.code.code_display.selection_toolbar import (
    SelectionToolbar,
)


class CodeSelectionHandle(SelectionDragHandle):
    """The selection grip of a code block."""

    handle_size = NumericProperty("22dp")
    touch_target_scale = NumericProperty(1.5)


class SelectionOverlay(EventDispatcher):
    """Two grips and a toolbar floating above the text while a
    selection is active. The overlay fans visible_rect out to both
    grips and re-dispatches their events.
    """

    __events__ = (
        "on_handle_pressed",
        "on_handle_moved",
        "on_handle_released",
        "on_copy_requested",
    )

    grip_start: ObjectProperty[CodeSelectionHandle] = ObjectProperty(None)
    grip_end: ObjectProperty[CodeSelectionHandle] = ObjectProperty(None)

    toolbar_pos: ObjectProperty[tuple[float, float] | None] = ObjectProperty(
        None, allownone=True
    )

    visible_rect: ObjectProperty[tuple[float, float, float, float] | None] = (
        ObjectProperty(None, allownone=True)
    )
    """Window rect a tip must land in for its grip to show; None
    while the text is scrolled out of view."""

    toolbar: ObjectProperty[SelectionToolbar] = ObjectProperty(None)

    flash_pill: ObjectProperty[FlashPill] = ObjectProperty(None)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.grip_start = self.build_grip(HandleRole.start)
        self.grip_end = self.build_grip(HandleRole.end)
        toolbar = SelectionToolbar()
        toolbar.bind(on_release=self.route_copy)
        self.toolbar = toolbar
        pill = FlashPill(text="Copied")
        pill.background_color = THEME_COLORS["CodeToolbar"]
        self.flash_pill = pill
        self.fbind("toolbar_pos", self.place_toolbar)

    def build_grip(self, role: HandleRole) -> CodeSelectionHandle:
        grip = CodeSelectionHandle(role=role)
        self.fbind("visible_rect", grip.setter("visible_rect"))
        grip.bind(
            on_handle_pressed=self.route_press,
            on_handle_moved=self.route_move,
            on_handle_released=self.route_release,
        )
        return grip

    def clear(self) -> None:
        self.grip_start.pointer_tip_pos = None
        self.grip_start.follows_drag = False
        self.grip_end.pointer_tip_pos = None
        self.grip_end.follows_drag = False
        self.toolbar_pos = None
        self.flash_pill.dismiss()

    # -- state, applied to the window --

    def place_toolbar(self, instance: object, pos: tuple[float, float] | None) -> None:
        """Mount the toolbar at pos, or unmount it for None."""
        if pos is None:
            self.unmount(self.toolbar)
            return
        self.toolbar.pos = pos
        self.mount(self.toolbar)

    def mount(self, widget: Widget) -> None:
        from kivy.core.window import Window

        if widget.parent is None:
            Window.add_widget(widget, canvas="after")

    def unmount(self, widget: Widget) -> None:
        from kivy.core.window import Window

        if widget.parent is not None:
            Window.remove_widget(widget)

    def point_on_overlay(self, x: float, y: float) -> bool:
        """Whether a window point lands on a mounted child."""
        return any(
            widget.parent is not None and widget.collide_point(x, y)
            for widget in (self.grip_start, self.grip_end, self.toolbar)
        )

    # -- child events, re-dispatched --

    def route_press(self, handle: SelectionDragHandle) -> None:
        self.dispatch("on_handle_pressed", handle.role)

    def route_move(self, handle: SelectionDragHandle, x: float, y: float) -> None:
        self.dispatch("on_handle_moved", handle.role, x, y)

    def route_release(self, handle: SelectionDragHandle) -> None:
        self.dispatch("on_handle_released", handle.role)

    def route_copy(self, toolbar: SelectionToolbar) -> None:
        self.dispatch("on_copy_requested")
        self.flash_pill.flash()

    def on_handle_pressed(self, role: HandleRole) -> None:
        """A touch landed on the grip that drags `role`; no drag yet."""

    def on_handle_moved(self, role: HandleRole, x: float, y: float) -> None:
        """Each window position of the grabbed grip."""

    def on_handle_released(self, role: HandleRole) -> None:
        """The touch on a grip lifted."""

    def on_copy_requested(self) -> None:
        """The toolbar was tapped."""


__all__ = ["CodeSelectionHandle", "SelectionOverlay", "SelectionToolbar"]
