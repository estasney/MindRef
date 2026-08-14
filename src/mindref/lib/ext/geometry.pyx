# cython: language_level=3, cdivision=True, embedsignature=True

from libc.math cimport M_PI, atan2, cos, fabs, floor, remainder, sin, fmin


def expand_tabs(str line not None, int tab_width):
    return line.replace("\t", " " * tab_width)


def prefix_width(object measurer, str line not None, int col, int tab_width):
    """Width of the line up to, not including, the column."""
    return measurer.width(expand_tabs(line[:col], tab_width))


def column_at(object measurer, str line not None, int tab_width, double x):
    """The caret column nearest to an x offset into the line."""
    cdef Py_ssize_t col
    cdef double previous, current
    cdef bint near_current
    if x <= 0:
        return 0
    previous = 0.0
    for col in range(1, len(line) + 1):
        current = measurer.width(expand_tabs(line[:col], tab_width))
        if current >= x:
            near_current = (current - x) <= (x - previous)
            return col if near_current else col - 1
        previous = current
    return len(line)


def row_at(double y_from_top, double line_height, int row_count):
    """The row under a y offset measured downward from the first line."""
    cdef double row
    if line_height <= 0 or row_count <= 0:
        return 0
    row = floor(y_from_top / line_height)
    if row < 0:
        return 0
    if row > row_count - 1:
        return row_count - 1
    return <int> row


cdef int group_of(str character):
    """0 for word characters, 1 for whitespace, 2 for symbols."""
    if character.isalnum() or character == "_":
        return 0
    if character.isspace():
        return 1
    return 2


def word_range(str line not None, int col):
    """Bounds of the character group at a column: word characters and
    whitespace group with their own kind; anything else stands alone."""
    cdef Py_ssize_t length, start, end
    cdef int kind
    length = len(line)
    if length == 0:
        return (0, 0)
    if col < 0:
        col = 0
    if col > length - 1:
        col = <int> (length - 1)
    kind = group_of(line[col])
    if kind == 2:
        return (col, col + 1)
    start = col
    while start > 0 and group_of(line[start - 1]) == kind:
        start -= 1
    end = col + 1
    while end < length and group_of(line[end]) == kind:
        end += 1
    return (start, end)


def order_cells(tuple a, tuple b):
    return (a, b) if a <= b else (b, a)


def row_spans(object lines, tuple start, tuple end):
    """(row, first column, last column) per row of an ordered range."""
    cdef list spans = []
    cdef Py_ssize_t row, start_row, end_row
    start_row = start[0]
    end_row = end[0]
    for row in range(start_row, end_row + 1):
        first = start[1] if row == start_row else 0
        last = end[1] if row == end_row else len(lines[row])
        spans.append((row, first, last))
    return spans


cpdef double joint_radius(double own, double neighbor, double radius):
    """Arc radius where two row edges meet at a step. Both rows draw
    an arc into the step, so each arc clamps to half of it; a step too
    small to see draws none."""
    cdef double step = fabs(own - neighbor)
    if step < 1.0:
        return 0.0
    return min(radius, step / 2.0)


cpdef bint edge_protrudes(double own, double neighbor, double side):
    """Whether an edge extends past the neighbor row's edge, away from
    the selection body. side is -1.0 for a left edge, +1.0 for a right
    edge."""
    return (own - neighbor) * side > 0


cpdef bint neighbor_reaches(double own, tuple neighbor, double side):
    """Whether the neighbor row spans across a recessed edge, so a
    concave flare there has neighbor selection to merge into."""
    if side > 0:
        return <double> neighbor[0] <= own
    return <double> neighbor[1] >= own


cdef double rounding(double own, tuple neighbor, double side, double radius):
    """Radius for one corner of a row; see corner_radii."""
    cdef double edge, arc
    if neighbor is None:
        return radius
    edge = neighbor[0] if side < 0 else neighbor[1]
    arc = joint_radius(own, edge, radius)
    if arc == 0.0:
        return 0.0
    if edge_protrudes(own, edge, side):
        return arc
    return 0.0 if neighbor_reaches(own, neighbor, side) else arc


def corner_radii(object edges, Py_ssize_t index, double radius):
    """Corner rounding for one row of a multi-row selection, ordered
    as RoundedRectangle expects: top-left, top-right, bottom-right,
    bottom-left. An outer corner, with no neighbor row, takes the full
    radius. At a step between rows only the protruding corner rounds;
    the recessed corner squares off and corner_fillets flares it into
    the neighbor. A recessed corner the neighbor does not span across
    has nothing to flare into and rounds instead."""
    cdef double x0, x1
    cdef tuple above = None, below = None
    x0, x1 = edges[index]
    if index > 0:
        above = edges[index - 1]
    if index + 1 < len(edges):
        below = edges[index + 1]
    return [
        rounding(x0, above, -1.0, radius),
        rounding(x1, above, 1.0, radius),
        rounding(x1, below, 1.0, radius),
        rounding(x0, below, -1.0, radius),
    ]


cdef class ConcaveFillet:
    """A quarter-circle flare filling the notch where a recessed row
    edge meets a longer neighbor row: the square between corner and
    center, minus the quarter disc around center."""

    cdef readonly tuple corner
    cdef readonly tuple center

    def __init__(self, tuple corner, tuple center):
        self.corner = corner
        self.center = center


cdef void collect_fillet(
    list fillets,
    double own,
    tuple neighbor,
    double side,
    double boundary_y,
    double inward_y,
    double radius,
):
    """Append the flare for one recessed corner; see corner_fillets."""
    cdef double edge, arc
    if neighbor is None:
        return
    edge = neighbor[0] if side < 0 else neighbor[1]
    arc = joint_radius(own, edge, radius)
    if arc == 0.0 or edge_protrudes(own, edge, side):
        return
    if not neighbor_reaches(own, neighbor, side):
        return
    fillets.append(
        ConcaveFillet(
            (own, boundary_y),
            (own + side * arc, boundary_y + inward_y * arc),
        )
    )


def corner_fillets(
    object edges,
    Py_ssize_t index,
    double radius,
    double y_top,
    double y_bottom,
):
    """Concave flares for the recessed corners of one row: the
    counterpart of corner_radii for the corners it squares off."""
    cdef double x0, x1
    cdef tuple above = None, below = None
    cdef list fillets = []
    x0, x1 = edges[index]
    if index > 0:
        above = edges[index - 1]
    if index + 1 < len(edges):
        below = edges[index + 1]
    collect_fillet(fillets, x0, above, -1.0, y_top, -1.0, radius)
    collect_fillet(fillets, x1, above, 1.0, y_top, -1.0, radius)
    collect_fillet(fillets, x1, below, 1.0, y_bottom, 1.0, radius)
    collect_fillet(fillets, x0, below, -1.0, y_bottom, 1.0, radius)
    return fillets


def fillet_fan(ConcaveFillet fillet, int segments=6):
    """Triangle-fan points for a concave fillet: the corner first,
    then the arc from the point beside the corner on the row edge to
    the point beside it on the row boundary."""
    cdef double corner_x, corner_y, center_x, center_y
    cdef double arc, start, sweep, angle
    cdef int count
    cdef list points
    corner_x, corner_y = fillet.corner
    center_x, center_y = fillet.center
    arc = fabs(center_x - corner_x)
    start = atan2(0.0, corner_x - center_x)
    sweep = remainder(atan2(corner_y - center_y, 0.0) - start, 2 * M_PI)
    points = [fillet.corner]
    for count in range(segments + 1):
        angle = start + sweep * count / segments
        points.append((center_x + arc * cos(angle), center_y + arc * sin(angle)))
    return points


def text_of_range(object lines, tuple start, tuple end):
    cdef list parts = []
    for row, first, last in row_spans(lines, start, end):
        parts.append(lines[row][first:last])
    return "\n".join(parts)


def widest_width(object measurer, object lines, int tab_width):
    cdef double widest = 0.0
    cdef double width
    for line in lines:
        width = measurer.width(expand_tabs(line, tab_width))
        if width > widest:
            widest = width
    return widest
