from __future__ import annotations

from dataclasses import dataclass
from functools import cache, partial

from kivy import Logger
from kivy._clock import ClockEvent
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.text.markup import MarkupLabel
from kivy.graphics import Color, InstructionGroup, Mesh, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.input import MotionEvent
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.parser import parse_color
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from pygments import highlight
from pygments.formatters import BBCodeFormatter
from pygments.lexer import Lexer
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.style import Style
from pygments.token import Token
from pygments.util import ClassNotFound

from mindref.lib.ext.geometry import (
    ConcaveFillet,
    column_at,
    corner_fillets,
    corner_radii,
    expand_tabs,
    fillet_fan,
    order_cells,
    prefix_width,
    row_at,
    row_spans,
    text_of_range,
    widest_width,
    word_range,
)
from mindref.lib.widgets.markdown.code.code_display.active_selection import (
    ActiveSelectionBehavior,
)
from mindref.lib.widgets.markdown.code.code_display.enums import HandleRole
from mindref.lib.widgets.markdown.code.code_display.geometry import TextMeasurer
from mindref.lib.widgets.markdown.code.code_display.jetbrains_dark import JetBrainsDark
from mindref.lib.widgets.markdown.code.code_display.selection_overlay import (
    SelectionOverlay,
)

Builder.load_string("""
<CodeDisplay>:
    font_name: app.fonts['mono']
    font_size: sp(app.base_font_size - 4)
""")


@cache
def resolve_lexer(name: str) -> Lexer:
    """Lexer for a fence language name; blank or unknown names fall
    back to markdown. Cached so equal fences share one instance."""
    normalized = name.strip() or "markdown"
    try:
        return get_lexer_by_name(normalized)
    except ClassNotFound:
        Logger.warning(f"Unknown lexer {normalized} - falling back to markdown")
        return get_lexer_by_name("markdown")


def fillet_mesh(fillet: ConcaveFillet) -> Mesh:
    """Canvas instruction for one concave selection fillet."""
    points = fillet_fan(fillet)
    vertices = [
        coordinate
        for point_x, point_y in points
        for coordinate in (point_x, point_y, 0.0, 0.0)
    ]
    return Mesh(
        vertices=vertices,
        indices=list(range(len(points))),
        mode="triangle_fan",
    )


@dataclass(frozen=True)
class SelectionGeometry:
    """Per-row extents of a selection, in widget coordinates."""

    spans: list[tuple[int, int, int]]
    """(row, first column, last column) for each selected row."""

    edges: list[tuple[float, float]]
    """Left and right x of the highlight on each selected row."""

    top: float
    """y of the top of the first text row."""

    line_height: float

    def row_top(self, index: int) -> float:
        return self.top - self.spans[index][0] * self.line_height

    def start_tip(self) -> tuple[float, float]:
        """Bottom-left corner of the first selected cell."""
        return (self.edges[0][0], self.row_top(0) - self.line_height)

    def end_tip(self) -> tuple[float, float]:
        """Bottom-right corner of the last selected cell."""
        return (self.edges[-1][1], self.row_top(-1) - self.line_height)


class CodeDisplay(ActiveSelectionBehavior, Widget):
    """
    Displays code with pygments highlighting.

    :Events:
        `on_double_tap`: (row, col)
            Fired on a double tap. The default handler selects the word
            at the cell.
        `on_long_press`: (row, col)
            Fired when a touch is held past long_press_delay. The
            default handler selects the word at the cell.
    """

    __events__ = ("on_double_tap", "on_long_press")

    text = StringProperty()
    lexer: ObjectProperty[Lexer] = ObjectProperty(PythonLexer())
    lexer_name = StringProperty()
    style: ObjectProperty[type[Style]] = ObjectProperty(JetBrainsDark)
    font_name = StringProperty()
    font_size = NumericProperty()
    tab_width = NumericProperty(4)
    padding = VariableListProperty([0, 0, 0, 0])
    mipmap = BooleanProperty(defaultvalue=True)

    selection_radius = NumericProperty("3dp")
    long_press_delay = NumericProperty(0.5)
    toolbar_gap = NumericProperty("8dp")
    """Vertical distance between the selection and the toolbar."""

    toolbar_margin = NumericProperty("4dp")
    """Minimum distance between the toolbar and the visible bounds."""

    selection_anchor: ObjectProperty[tuple[int, int] | None] = ObjectProperty(
        None, allownone=True
    )
    selection_head: ObjectProperty[tuple[int, int] | None] = ObjectProperty(
        None, allownone=True
    )
    drag_pos: ObjectProperty[tuple[float, float] | None] = ObjectProperty(
        None, allownone=True
    )
    touch_down_cell: ObjectProperty[tuple[int, int] | None] = ObjectProperty(
        None, allownone=True
    )
    enclosing_scrollers: ListProperty[ScrollView] = ListProperty([])
    measurer: ObjectProperty[TextMeasurer] = ObjectProperty(None)

    def __init__(self, **kwargs: object) -> None:
        """Create clock triggers for retexturing and overlay placement;
        bind them to the properties that invalidate each."""
        self.retexture_trigger = Clock.create_trigger(self.render_lines, -1)
        self.layout_trigger = Clock.create_trigger(self.layout_lines, -1)
        self.overlay_trigger = Clock.create_trigger(self.update_selection_overlay, -1)
        super().__init__(**kwargs)

        self.long_press_event: ClockEvent | None = None
        self.autoscroll_event: ClockEvent | None = None
        self.bound_scrollers: list[ScrollView] = []

        self.formatter: BBCodeFormatter[str] = BBCodeFormatter(style=self.style)
        self.line_textures: list[Texture | None] = []
        self.line_rects: list[Rectangle] = []

        self.overlay = SelectionOverlay()
        self.overlay.bind(
            on_handle_pressed=self.apply_handle_press,
            on_handle_moved=self.apply_handle_move,
            on_handle_released=self.apply_handle_release,
            on_copy_requested=self.apply_copy_request,
        )

        self.selection_group = InstructionGroup()
        self.text_group = InstructionGroup()
        self.canvas.add(self.selection_group)
        self.canvas.add(self.text_group)

        fbind = self.fbind
        fbind("render_signature", self.retexture_trigger)
        fbind("pos", self.layout_trigger)
        fbind("size", self.layout_trigger)
        fbind("padding", self.layout_trigger)
        fbind("pos", self.overlay_trigger)
        fbind("size", self.overlay_trigger)
        fbind("selection_anchor", self.overlay_trigger)
        fbind("selection_head", self.overlay_trigger)
        fbind("drag_pos", self.overlay_trigger)
        fbind("selection_radius", self.overlay_trigger)
        fbind("toolbar_gap", self.overlay_trigger)
        fbind("toolbar_margin", self.overlay_trigger)

    def on_active(self, instance: object, value: bool) -> None:
        """Activation collects the enclosing scrollers; deactivation
        clears the drag, selection, overlay, and scrollers."""
        if value:
            self.enclosing_scrollers = self.collect_enclosing_scrollers()
            return
        self.drag_pos = None
        self.clear_selection()
        self.overlay.clear()
        self.enclosing_scrollers = []

    def on_enclosing_scrollers(self, instance: object, value: list[ScrollView]) -> None:
        for scroller in self.bound_scrollers:
            scroller.funbind("scroll_x", self.overlay_trigger)
            scroller.funbind("scroll_y", self.overlay_trigger)
        for scroller in value:
            scroller.fbind("scroll_x", self.overlay_trigger)
            scroller.fbind("scroll_y", self.overlay_trigger)
        self.bound_scrollers = list(value)

    def on_text(self, instance: object, value: str) -> None:
        self.active = False

    def get_lines(self):
        return self.text.split("\n")

    lines: AliasProperty[list[str]] = AliasProperty(
        get_lines, bind=("text",), cache=True
    )

    def on_lexer_name(self, instance: object, value: str) -> None:
        self.lexer = resolve_lexer(value)

    def on_style(self, instance: object, value: type[Style]) -> None:
        self.formatter = BBCodeFormatter(style=value)

    def on_parent(self, instance: object, parent: object) -> None:
        if parent is None:
            self.active = False
            return
        self.retexture_trigger()

    def get_measurer_font(self) -> tuple[str, float]:
        return (self.font_name, float(self.font_size))

    measurer_font: AliasProperty[tuple[str, float]] = AliasProperty(
        get_measurer_font, bind=("font_name", "font_size"), cache=True
    )

    def on_measurer_font(self, instance: object, value: tuple[str, float]) -> None:
        self.measurer = TextMeasurer(*value)

    def get_render_signature(self) -> tuple[object, ...]:
        return (
            self.text,
            self.lexer,
            self.style,
            self.font_name,
            float(self.font_size),
            int(self.tab_width),
            self.mipmap,
        )

    render_signature: AliasProperty[tuple[object, ...]] = AliasProperty(
        get_render_signature,
        bind=(
            "text",
            "lexer",
            "style",
            "font_name",
            "font_size",
            "tab_width",
            "mipmap",
        ),
        cache=True,
    )

    def style_text_color(self) -> str:
        color = self.style.style_for_token(Token.Text).get("color")
        return f"#{color}" if color else "#FFFFFF"

    def render_markup(self, line: str) -> str:
        """Transform a line into bbcode markup"""
        if not line:
            return ""
        expanded = expand_tabs(line, int(self.tab_width))
        escaped = expanded.replace("[", "\x01").replace("]", "\x02")
        highlighted = highlight(escaped, self.lexer, self.formatter)
        restored = highlighted.replace("\x01", "&bl;").replace("\x02", "&br;")
        colored = f"[color={self.style_text_color()}]{restored}[/color]"
        return colored.replace("\n", "").replace("[u]", "").replace("[/u]", "")

    def line_texture(self, line: str) -> Texture | None:
        markup = self.render_markup(line)
        if not markup:
            return None
        label = MarkupLabel(
            text=markup,
            font_name=self.font_name,
            font_size=self.font_size,
            mipmap=self.mipmap,
        )
        label.refresh()
        return label.texture

    def render_lines(self, *args: object) -> None:
        """Rebuild the per-line textures and the canvas instructions"""
        lines = self.lines
        self.line_textures = [self.line_texture(line) for line in lines]
        group = self.text_group
        group.clear()
        self.line_rects = []
        group.add(Color(1, 1, 1, 1))
        for texture in self.line_textures:
            rect = Rectangle(texture=texture)
            self.line_rects.append(rect)
            group.add(rect)
        self.layout_lines()

    def layout_lines(self, *args: object) -> None:
        """Place the line rectangles against the widget's position and
        padding."""
        line_height = self.measurer.line_height
        left = self.x + self.padding[0]
        top = self.top - self.padding[1]
        rows = zip(self.line_textures, self.line_rects, strict=True)
        for row, (texture, rect) in enumerate(rows):
            if texture is None:
                rect.size = (0, 0)
                continue
            rect.size = texture.size
            rect.pos = (left, top - row * line_height - texture.height)
        self.overlay_trigger()

    # -- geometry --

    def cell_at(self, x: float, y: float) -> tuple[int, int]:
        """Row and column under a point in widget coordinates.

        Points beyond a line end clamp to the line end; points above or
        below the text clamp to the first or last line.
        """
        measurer = self.measurer
        lines = self.lines
        y_from_top = (self.top - self.padding[1]) - y
        row = row_at(y_from_top, measurer.line_height, len(lines))
        col = column_at(
            measurer, lines[row], int(self.tab_width), x - self.x - self.padding[0]
        )
        return (row, col)

    def collect_enclosing_scrollers(self) -> list[ScrollView]:
        """Every ScrollView above this widget, innermost first."""
        scrollers: list[ScrollView] = []
        widget = self.parent
        while isinstance(widget, Widget):
            if isinstance(widget, ScrollView):
                scrollers.append(widget)
            widget = widget.parent
        return scrollers

    def clip_to_scrollers(
        self, left: float, bottom: float, right: float, top: float
    ) -> tuple[float, float, float, float]:
        """Cut a window-coordinate rectangle down to the bounds of every
        enclosing scroller."""
        for scroller in self.enclosing_scrollers:
            s_left, s_bottom = scroller.to_window(scroller.x, scroller.y)
            s_right, s_top = scroller.to_window(scroller.right, scroller.top)
            left, bottom = max(left, s_left), max(bottom, s_bottom)
            right, top = min(right, s_right), min(top, s_top)
        return (left, bottom, right, top)

    def visible_window_rect(self) -> tuple[float, float, float, float] | None:
        """On-screen part of this widget in window coordinates; None
        when scrolled fully out of view."""
        win_x, win_y = self.to_window(self.x, self.y)
        win_right, win_top = self.to_window(self.right, self.top)
        left, bottom, right, top = self.clip_to_scrollers(
            win_x, win_y, win_right, win_top
        )
        if right <= left or top <= bottom:
            return None
        return (left, bottom, right, top)

    # -- selection --

    def select_range(self, anchor: tuple[int, int], head: tuple[int, int]) -> None:
        self.selection_anchor = anchor
        self.selection_head = head
        self.active = True

    def select_word_at(self, row: int, col: int) -> None:
        lines = self.lines
        row = min(max(row, 0), len(lines) - 1)
        start, end = word_range(lines[row], col)
        if start == end:
            return
        self.select_range((row, start), (row, end))

    def select_all(self) -> None:
        lines = self.lines
        self.select_range((0, 0), (len(lines) - 1, len(lines[-1])))

    def clear_selection(self) -> None:
        self.selection_anchor = None
        self.selection_head = None

    def get_selection_text(self) -> str:
        anchor = self.selection_anchor
        head = self.selection_head
        if anchor is None or head is None:
            return ""
        start, end = order_cells(anchor, head)
        return text_of_range(self.lines, start, end)

    selection_text = AliasProperty(
        get_selection_text, None, bind=("selection_anchor", "selection_head", "text")
    )
    """The selected string, empty when nothing is selected."""

    def copy_selection(self) -> None:
        """Place the selection on the system clipboard."""
        text = self.selection_text
        if text:
            Clipboard.copy(text)

    # -- input --

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """Start a drag selection on a plain touch; dispatch
        on_double_tap on a double tap; arm the long-press clock."""
        if not self.collide_point(*touch.pos):
            return False
        # A ScrollView above re-simulates the down on release; accept
        # each touch once.
        if touch.ud.get("code_display_press") is self:
            return True
        touch.ud["code_display_press"] = self
        if touch.is_double_tap:
            self.touch_down_cell = None
            cell = self.cell_at(*touch.pos)
            self.dispatch("on_double_tap", cell)
            return True
        touch.grab(self)
        self.touch_down_cell = self.cell_at(*touch.pos)
        self.long_press_event = Clock.schedule_once(
            partial(self.apply_long_press, self.to_window(*touch.pos)),
            self.long_press_delay,
        )
        return True

    def apply_long_press(self, pos: tuple[float, float], dt: float) -> None:
        """Dispatch on_long_press. The hold starts a drag, so the held
        position seeds drag_pos."""
        if self.touch_down_cell is not None:
            self.drag_pos = pos
            self.dispatch("on_long_press", self.touch_down_cell)

    def on_double_tap(self, cell: tuple[int, int]) -> None:
        self.select_word_at(*cell)

    def on_long_press(self, cell: tuple[int, int]) -> None:
        self.select_word_at(*cell)

    def cancel_long_press(self) -> None:
        if self.long_press_event is not None:
            self.long_press_event.cancel()
            self.long_press_event = None

    def on_touch_move(self, touch: MotionEvent) -> bool:
        """Extend the selection head character by character."""
        if touch.grab_current is not self or self.touch_down_cell is None:
            return False
        # Grab dispatch delivers the touch in parent coordinates already.
        head = self.cell_at(*touch.pos)

        if self.drag_pos is not None or head != self.touch_down_cell:
            self.cancel_long_press()
            self.select_range(self.touch_down_cell, head)
            self.drag_pos = self.to_window(*touch.pos)
        return True

    def on_touch_up(self, touch: MotionEvent) -> bool:
        """A plain release without a selection deactivates."""
        if touch.grab_current is not self:
            Logger.info(f"CodeDisplay: up uid={touch.uid} ignored - not grabbed")
            return False
        touch.ungrab(self)
        self.cancel_long_press()
        # A ScrollView above re-simulates downs and delays ups; only a
        # release whose press this widget saw may deactivate.
        if self.touch_down_cell is not None and self.drag_pos is None:
            self.active = False
        self.touch_down_cell = None
        self.drag_pos = None
        return True

    # -- active-selection contract --

    def selection_hit(self, touch: MotionEvent) -> bool:
        """The widget or a mounted overlay child. This runs before the
        window dispatches to the children; a miss would unmount them
        under the touch."""
        if self.overlay.point_on_overlay(*touch.pos):
            return True
        return self.collide_point(*self.to_widget(*touch.pos))

    # -- handle drag --

    def apply_handle_press(self, overlay: SelectionOverlay, role: HandleRole) -> None:
        """The grabbed end becomes the head; the first move seeds
        drag_pos."""
        anchor = self.selection_anchor
        head = self.selection_head
        if anchor is None or head is None:
            return
        match role:
            case HandleRole.start:
                self.selection_head, self.selection_anchor = order_cells(anchor, head)
            case HandleRole.end:
                self.selection_anchor, self.selection_head = order_cells(anchor, head)

    def apply_handle_move(
        self, overlay: SelectionOverlay, role: HandleRole, x: float, y: float
    ) -> None:
        """Follow the pointer with the selection head."""
        if self.selection_anchor is None:
            return
        self.drag_pos = (x, y)
        self.selection_head = self.cell_at(*self.to_widget(x, y))

    def apply_handle_release(self, overlay: SelectionOverlay, role: HandleRole) -> None:
        self.drag_pos = None

    def apply_copy_request(self, overlay: SelectionOverlay) -> None:
        self.copy_selection()

    def on_drag_pos(self, instance: object, value: tuple[float, float] | None) -> None:
        """The autoscroll clock runs while drag_pos holds a point."""
        match value, self.autoscroll_event:
            case None, ClockEvent() as event:
                event.cancel()
                self.autoscroll_event = None
            case tuple(), None:
                self.autoscroll_event = Clock.schedule_interval(
                    self.autoscroll_toward_drag, 0
                )
            case _:
                pass

    def autoscroll_toward_drag(self, dt: float) -> None:
        """Keep scrolling while the drag holds a scroller's edge band,
        so the selection can extend past visible content."""
        pos = self.drag_pos
        if pos is None:
            return
        moved = False
        for scroller in self.enclosing_scrollers:
            if self.nudge_scroll_at_edges(scroller, pos):
                moved = True
        if moved:
            self.selection_head = self.cell_at(*self.to_widget(*pos))

    def nudge_scroll_at_edges(
        self, scroller: ScrollView, pos: tuple[float, float]
    ) -> bool:
        """Nudge the scroller on each axis whose edge band holds the
        window point; True when a scroll position changed."""
        left, bottom = scroller.to_window(scroller.x, scroller.y)
        right, top = scroller.to_window(scroller.right, scroller.top)
        band = dp(28)
        step_x, step_y = scroller.convert_distance_to_scroll(dp(6), dp(6))
        moved = False
        if scroller.do_scroll_x and scroller.viewport_size[0] > scroller.width:
            if pos[0] >= right - band and scroller.scroll_x < 1.0:
                scroller.scroll_x = min(1.0, scroller.scroll_x + step_x)
                moved = True
            elif pos[0] <= left + band and scroller.scroll_x > 0.0:
                scroller.scroll_x = max(0.0, scroller.scroll_x - step_x)
                moved = True
        if scroller.do_scroll_y and scroller.viewport_size[1] > scroller.height:
            if pos[1] >= top - band and scroller.scroll_y < 1.0:
                scroller.scroll_y = min(1.0, scroller.scroll_y + step_y)
                moved = True
            elif pos[1] <= bottom + band and scroller.scroll_y > 0.0:
                scroller.scroll_y = max(0.0, scroller.scroll_y - step_y)
                moved = True
        return moved

    def handle_window_key(
        self,
        window: object,
        key: int,
        scancode: int,
        codepoint: str | None,
        modifiers: list[str],
    ) -> bool:
        """Copy the selection on ctrl+c."""
        if key == ord("c") and "ctrl" in modifiers and self.selection_text:
            self.copy_selection()
            return True
        return False

    # -- selection overlay --

    def update_selection_overlay(self, *args: object) -> None:
        """Redraw the selection quads on the widget canvas and write
        the state the overlay places its grips and toolbar from."""
        self.selection_group.clear()
        geometry = self.selection_geometry()
        if geometry is None:
            self.overlay.clear()
            return
        self.draw_selection_quads(geometry)
        if not self.active:
            self.overlay.clear()
            return
        start_tip = self.to_window(*geometry.start_tip())
        end_tip = self.to_window(*geometry.end_tip())
        self.update_grips(start_tip, end_tip)
        self.overlay.toolbar_pos = self.toolbar_position(geometry, start_tip, end_tip)

    def selection_geometry(self) -> SelectionGeometry | None:
        """Per-row extents of the selection; None if no selection or
        its rows point past the text."""
        anchor = self.selection_anchor
        head = self.selection_head
        if anchor is None or head is None:
            return None
        lines = self.lines
        start, end = order_cells(anchor, head)
        if end[0] >= len(lines):
            return None
        measurer = self.measurer
        tab_width = int(self.tab_width)
        left = self.x + self.padding[0]
        spans = row_spans(lines, start, end)
        edges: list[tuple[float, float]] = []
        for row, first, last in spans:
            x0 = left + prefix_width(measurer, lines[row], first, tab_width)
            x1 = left + prefix_width(measurer, lines[row], last, tab_width)
            if x1 - x0 < 1:
                x1 = x0 + measurer.width(" ")
            edges.append((x0, x1))
        return SelectionGeometry(
            spans=spans,
            edges=edges,
            top=self.top - self.padding[1],
            line_height=measurer.line_height,
        )

    def draw_selection_quads(self, geometry: SelectionGeometry) -> None:
        """Fill selection_group with a rounded quad per selected row
        and the fillets that join adjacent rows."""
        quads = self.selection_group
        quads.add(Color(*parse_color(self.style.highlight_color)))
        edges = geometry.edges
        line_height = geometry.line_height
        radius = float(self.selection_radius)
        for index, (x0, x1) in enumerate(edges):
            y_top = geometry.row_top(index)
            quads.add(
                RoundedRectangle(
                    pos=(x0, y_top - line_height),
                    size=(x1 - x0, line_height),
                    radius=corner_radii(edges, index, radius),
                )
            )
            for fillet in corner_fillets(
                edges, index, radius, y_top, y_top - line_height
            ):
                quads.add(fillet_mesh(fillet))

    def dragged_role(self) -> HandleRole | None:
        """The selection end the current drag moves; None if no drag."""
        if self.drag_pos is None:
            return None
        anchor = self.selection_anchor
        head = self.selection_head
        if anchor is None or head is None:
            return None
        start = order_cells(anchor, head)[0]
        return HandleRole.start if head == start else HandleRole.end

    def update_grips(
        self, start_tip: tuple[float, float], end_tip: tuple[float, float]
    ) -> None:
        """Write the tips, visible rect, and drag flags the grips
        place themselves from."""
        dragged = self.dragged_role()
        overlay = self.overlay
        overlay.visible_rect = self.visible_window_rect()
        overlay.grip_start.follows_drag = dragged == HandleRole.start
        overlay.grip_end.follows_drag = dragged == HandleRole.end
        overlay.grip_start.pointer_tip_pos = start_tip
        overlay.grip_end.pointer_tip_pos = end_tip

    def toolbar_position(
        self,
        geometry: SelectionGeometry,
        start_tip: tuple[float, float],
        end_tip: tuple[float, float],
    ) -> tuple[float, float]:
        """Window position for the toolbar: above the selection, below
        it without room, always clamped into the visible scroll area."""
        bar_w, bar_h = self.overlay.toolbar.size
        gap = float(self.toolbar_gap)
        margin = float(self.toolbar_margin)
        from kivy.core.window import Window

        bounds = self.clip_to_scrollers(0.0, 0.0, Window.width, Window.height)
        left = self.x + self.padding[0]
        top_window = self.to_window(left, geometry.row_top(0))[1]
        bar_y = top_window + gap
        if bar_y + bar_h > bounds[3] - margin:
            bar_y = end_tip[1] - gap - bar_h
        bar_y = min(max(bar_y, bounds[1] + margin), bounds[3] - bar_h - margin)
        mid = (start_tip[0] + end_tip[0]) / 2
        bar_x = mid - bar_w / 2
        bar_x = min(max(bar_x, bounds[0] + margin), bounds[2] - bar_w - margin)
        return (bar_x, bar_y)

    # -- sizing contract for the enclosing scroller --

    def get_minimum_width(self) -> float:
        """Widest line plus horizontal padding."""
        measurer = self.measurer
        widest = widest_width(measurer, self.text.split("\n"), int(self.tab_width))
        return widest + self.padding[0] + self.padding[2]

    minimum_width = AliasProperty(
        get_minimum_width,
        bind=("text", "font_name", "font_size", "tab_width", "padding"),
        cache=True,
    )

    def get_minimum_height(self) -> float:
        """Line count times line height plus vertical padding."""
        line_count = len(self.text.split("\n"))
        line_height = self.measurer.line_height
        return line_count * line_height + self.padding[1] + self.padding[3]

    minimum_height = AliasProperty(
        get_minimum_height,
        bind=("text", "font_name", "font_size", "padding"),
        cache=True,
    )
