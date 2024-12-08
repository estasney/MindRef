# cython: language_level=3, cdivision=True, embedsignature=True

cdef inline double CLAMP(double x, double lower, double upper):
    return lower if x < lower else (upper if x > upper else x)

def normalize_coordinates(double touch_x, double touch_y, double self_x, double self_y, double self_height=0.0,
                          double self_width=0.0):
    cdef (double, double) result = (0.0, 0.0)

    if self_width == 0.0:
        return result

    result[0] = CLAMP((touch_x - self_x) / self_width, 0.0, 1.0)
    result[1] = CLAMP((1.0 - (touch_y - self_y) / self_height), 0.0, 1.0)

    return result

def compute_ref_coords(double width, double height, double wX, double wY, double texture_width, double texture_height,
                       double span_x1, double span_y1, double span_x2, double span_y2,
                       double hl_pad_x, double hl_pad_y):
    """
        Since spans are computed relative to texture, we need to convert them to widget coordinates

        Spans (x1, y1) references the top left corner of the texture. So x1 = 0, y1 = 0 means the
            top left corner of the texture is at the top left corner of the widget.
        Relative to texture, the y coordinate increases as you go down.

        Kivy's typical origin is (0,0) at bottom-left.

        ┌───────────────────────────────────────────────────────────────────────┐
        │                                 Parent                                │
        │   ┌───────────────────────────────────────────────────────────────┐   │
        │   │                             Label                             │   │
        │   │                                                               │   │
        │   │   ┌────────────────────────────────────────────────────────┐  │   │
        │   │   │                                                        │  │   │
        │   │   │                        Texture                         │  │   │
        │   │   └────────────────────────────────────────────────────────┘  │   │
        │   │                                                               │   │
        │   └───────────────────────────────────────────────────────────────┘   │
        │                                                                       │
        │                                                                       │
        └───────────────────────────────────────────────────────────────────────┘
    this is a long text snippet that will be used to test the text wrapping
    break

    refs : [4,0, 504, 22], [0, 22, 50, 44]

    """

    """
    X Coordinate
    For X coordinate, we only need to consider the left padding. Basically, we need the distance from the
        left edge of the widget to the left edge of the texture. This is the same as the left padding.
    """

    cdef double pX = (width - texture_width) / 2.0
    span_x1 += pX
    span_x2 += pX

    """
    Y Coordinate
    For Y coordinate, we need to consider the top padding and the height of the texture.
    Then we need to invert the y coordinate because the y coordinate increases as you go down.

    """
    cdef double pY = (height - texture_height) / 2.0
    # Convert span_y to be relative to the bottom of the widget.
    # Larger y means lower on the screen.
    span_y1 = height - span_y1 - pY
    span_y2 = height - span_y2 - pY

    """
    Highlight Padding
    We want the highlight padding to extend outside of the span. So for x1, we subtract the highlight padding.
    For x2, we add the highlight padding.
    For y1, we subtract the highlight padding.
    For y2, we add the highlight padding.
    """

    span_x1 -= hl_pad_x
    span_x2 += hl_pad_x
    span_y1 -= hl_pad_y
    span_y2 += hl_pad_y

    """
    Now we need to convert these into window coordinates using the widget's position and size
    """
    span_x1 += wX
    span_x2 += wX
    span_y1 += wY
    span_y2 += wY

    return span_x1, span_y1, span_x2, span_y2

def color_str_components(color_str : str):
    """Convert hex color string to rgba float components"""
    cdef float r, g, b, a
    color_str = color_str.removeprefix('#')

    cdef bint has_opacity = len(color_str) > 6
    cdef int colorInt = int(color_str, 16)
    r = ((colorInt >> 16) & 0xFF) / 255.0
    g = ((colorInt >> 8) & 0xFF) / 255.0
    b = (colorInt & 0xFF) / 255.0
    a = ((colorInt >> 24) & 0xFF) / 255.0 if has_opacity else 1.0
    return r, g, b, a

cdef float compute_brightness(float r, float g, float b, float a):
    """Compute brightness of a color"""

    return (r * 0.299 + g * 0.587 + b * 0.114 + (1.0 - a)) * 255.0

cdef float compute_mixed_brightness(float r1, float g1, float b1, float a1, float r2, float g2, float b2, float a2):
    """Compute brightness of two colors mixed together with alpha"""
    cdef float r, g, b, a
    a = 1.0 - (1.0 - a1) * (1.0 - a2)
    r = r1 * a1 / a + r2 * a2 * (1 - a1) / a
    g = g1 * a1 / a + g2 * a2 * (1 - a1) / a
    b = b1 * a1 / a + b2 * a2 * (1 - a1) / a
    return compute_brightness(r, g, b, a)

def compute_text_contrast(background_color: tuple[float, float, float, float], threshold: float,
                          highlight_color: tuple[float, float, float, float] = None):
    """

    Parameters
    ----------
    background_color : tuple[float, float, float, float]
        Background color of the widget
    threshold : float
        Threshold for contrast
    highlight_color : Optional[tuple[float, float, float, float]], optional
        Highlight color of the widget, by default None

    Returns
    -------

    """
    if highlight_color is None:
        brightness = compute_brightness(background_color[0], background_color[1], background_color[2],
                                        background_color[3])
    else:
        brightness = compute_mixed_brightness(background_color[0], background_color[1], background_color[2],
                                              background_color[3],
                                              highlight_color[0], highlight_color[1], highlight_color[2],
                                              highlight_color[3])
    if brightness > threshold:
        return '#000000'
    else:
        return '#ffffff'

def compute_overscroll(overscroll, target_height, overscroll_threshold,
                       overscroll_refresh_threshold, min_opacity):
    """
    Given our thresholds and target height, determine if:
        - We have overscrolled enough to adjust opacity
        - If so, compute the opacity
        - If overscrolled enough to trigger a refresh
    """
    cdef double overscroll_, target_height_, overscroll_threshold_
    overscroll_ = overscroll
    target_height_ = target_height
    overscroll_threshold_ = overscroll_threshold
    # If overscroll is positive or target height is zero, we're not overscrolled
    if overscroll_ >= 0.0 or target_height_ == 0.0 or overscroll_threshold_ <= 0.0:
        return 1.0, False

    # Calculate our overscroll percentage which is the absolute value of the overscroll divided by the height of the
    # target widget
    cdef double overscroll_pct_ = (-1.0 * overscroll_) / target_height_

    # If our overscroll_pct is less than the overscroll_threshold, we can quit early
    if overscroll_pct_ < overscroll_threshold_:
        return 1.0, False

    # Now we know we're going to affect the opacity of the target widget
    # Opacity will begin decreasing at the overscroll_threshold and will be self.min_opacity at the overscroll_refresh_threshold
    # We'll use a linear interpolation to calculate the opacity
    cdef double overscroll_refresh_threshold_ = overscroll_refresh_threshold
    cdef double min_opacity_ = min_opacity
    cdef double opacity_
    opacity_ = 1.0 - (overscroll_pct_ - overscroll_threshold_) / (
            overscroll_refresh_threshold_ - overscroll_threshold_)
    opacity_ = opacity_ if opacity_ > min_opacity_ else min_opacity_

    # Determine if we've overscrolled enough to trigger a refresh
    if overscroll_pct_ >= overscroll_refresh_threshold_:
        return opacity_, True
    else:
        return opacity_, False

cdef class RollingIndex:
    """
    Implements rolling index so that we can always call 'next' or 'previous'

    As with `range`, `end` is not inclusive
    """

    def __init__(self, size, current=0):
        self._size = size
        self._start = 0
        self._end = size - 1 if size > 0 else 0
        self._current = current

    cdef bint _set_current(self, int n):
        if n > self._size:
            return False
        self._current = n
        return True

    @property
    def size(self):
        return self._size

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, n):
        if not self._set_current(n):
            raise IndexError(f"{n} is greater than {self._size}")

    cdef int _next(self, bint peek):
        cdef int next_index
        next_index = self._current + 1
        if next_index > self._end:
            next_index = 0
        if peek:
            return next_index
        self._current = next_index
        return next_index

    def next(self, peek=False):
        cdef bint flag
        flag = True if peek else False
        return self._next(flag)

    cdef int _prev(self, bint peek):
        cdef int prev_index
        prev_index = self._current - 1
        if prev_index < self._start:
            prev_index = self._end
        if peek:
            return prev_index
        self._current = prev_index
        return prev_index

    def previous(self, peek=False):
        cdef bint flag
        flag = True if peek else False
        return self._prev(flag)
