from __future__ import annotations

from kivy.lang import Builder
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.widget import Widget

from mindref.lib.widgets.behavior.handle_drag_behavior import HandleDragBehavior
from mindref.lib.widgets.markdown.code.code_display.enums import HandleRole

Builder.load_string("""
<SelectionDragHandle>:
    size_hint: None, None
    handle_color: app.colors['SelectionGrip']
    canvas:
        Color:
            rgba: self.handle_color
        Ellipse:
            pos: self.pos
            size: self.size
        Rectangle:
            pos: (self.center_x, self.center_y) if self.role == "start" else (self.x, self.center_y)
            size: self.width / 2, self.height / 2
""")


class SelectionDragHandle(HandleDragBehavior, Widget):
    """A draggable grip for one end of a text selection."""

    role: OptionProperty[HandleRole] = OptionProperty(
        HandleRole.start, options=tuple(HandleRole)
    )

    pointer_tip_pos: ObjectProperty[tuple[float, float] | None] = ObjectProperty(
        None, allownone=True
    )

    visible_rect: ObjectProperty[tuple[float, float, float, float] | None] = (
        ObjectProperty(None, allownone=True)
    )
    """Window rect the tip must land in for the grip to show; None
    while the text is scrolled out of view."""

    dragging = BooleanProperty(False)
    """True while a touch holds the grip."""

    follows_drag = BooleanProperty(False)
    """True while a drag that started elsewhere moves this grip's
    selection end; the owner writes it. Either flag shows the grip
    outside visible_rect."""

    handle_color = ColorProperty()
    handle_size = NumericProperty("22dp")
    """Diameter of the grip circle, and the side of the widget box."""

    touch_target_scale = NumericProperty(1.5)
    """The hit circle is the drawn radius times this value."""

    def __init__(self, **kwargs: object) -> None:
        """Size the box to the grip and keep it square through
        handle_size changes."""
        super().__init__(**kwargs)
        self.size = (self.handle_size, self.handle_size)
        self.fbind("handle_size", self.apply_handle_size)

    # -- placement --

    def get_tip(self) -> tuple[float, float]:
        """The text-cell corner the grip points at, in parent
        coordinates: the top corner on the side the grip hangs from."""
        edge = self.right if self.role == HandleRole.start else self.x
        return (float(edge), float(self.top))

    def set_tip(self, value: tuple[float, float]) -> bool:
        """Hang the grip from a tip point."""
        tip_x, tip_y = value
        diameter = float(self.handle_size)
        left = tip_x - diameter if self.role == HandleRole.start else tip_x
        self.pos = (left, tip_y - diameter)
        return True

    tip = AliasProperty(get_tip, set_tip, bind=("pos", "size", "role"))
    """The text-cell corner the handle points at."""

    def apply_handle_size(self, instance: object, value: float) -> None:
        """Keep the widget box square with the grip circle, tip in
        place."""
        anchor = self.tip
        self.size = (value, value)
        self.tip = anchor

    # -- window presence --

    def get_should_show(self) -> bool:
        """Whether the grip belongs on the window: its tip is inside
        visible_rect, or a drag moves its selection end."""
        tip = self.pointer_tip_pos
        if tip is None:
            return False
        if self.dragging or self.follows_drag:
            return True
        rect = self.visible_rect
        return (
            rect is not None
            and rect[0] <= tip[0] <= rect[2]
            and rect[1] <= tip[1] <= rect[3]
        )

    should_show = AliasProperty(
        get_should_show,
        bind=("pointer_tip_pos", "visible_rect", "dragging", "follows_drag"),
        cache=True,
    )

    def on_pointer_tip_pos(
        self, instance: object, pos: tuple[float, float] | None
    ) -> None:
        if pos is not None:
            self.tip = pos

    def on_should_show(self, instance: object, should_show: bool) -> None:
        from kivy.core.window import Window

        if should_show:
            if self.parent is None:
                Window.add_widget(self, canvas="after")
        elif self.parent is not None:
            Window.remove_widget(self)

    def on_handle_pressed(self) -> None:
        self.dragging = True

    def on_handle_released(self) -> None:
        self.dragging = False

    # -- collision --

    def collide_point(self, x: float, y: float) -> bool:
        """The grip circle grown by touch_target_scale."""
        reach = float(self.handle_size) / 2 * float(self.touch_target_scale)
        dx = x - float(self.center_x)
        dy = y - float(self.center_y)
        return dx * dx + dy * dy <= reach * reach


__all__ = ["SelectionDragHandle"]
