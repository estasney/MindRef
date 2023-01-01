# cython: language_level=3, cdivision=True

def normalize_coordinates(double touch_x, double touch_y, double self_x, double self_y,
                          double self_height, double self_width):
    cdef double x_local, y_local

    if self_height != 0:

        x_local = (touch_x - self_x) / self_height
        x_local = 1.0 if x_local > 1.0 else x_local
        x_local = 0.0 if x_local < 0.0 else x_local
    else:
        x_local = 0.0

    if self_width != 0:
        y_local = 1.0 - (touch_y - self_y) / self_width
        y_local = 1.0 if y_local > 1.0 else y_local
        y_local = 0.0 if y_local < 0.0 else y_local
    else:
        y_local = 0.0

    return x_local, y_local

def compute_ref_coords(double center_x, double center_y, double texture_width, double texture_height,
                       double span_x1, double span_y1, double span_x2, double span_y2,
                       double hl_pad_x, double hl_pad_y):
    """
        Since spans are computed relative to texture, we want them in window form

        Spans (x1, y1) references the top left corner of the texture
        Spans y2 increases as it moves down

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
    """

    cdef double pX, pY

    pX = center_x - texture_width / 2.0
    pY = center_y - texture_height / 2.0

    span_x1 += pX
    span_x2 += pX
    span_y1 += pY
    span_y2 += pY

    span_x1 -= hl_pad_x
    span_x2 += hl_pad_x
    span_y1 += hl_pad_y
    span_y2 -= hl_pad_y

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
