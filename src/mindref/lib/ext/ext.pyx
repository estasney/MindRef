# cython: language_level=3, cdivision=True, embedsignature=True
from libc.math cimport pow

cdef inline double CLAMP(double x, double lower, double upper):
    return lower if x < lower else (upper if x > upper else x)


cdef inline double normalize_domain_range(double value, double lower, double upper):
    """
    Normalize a value to a range between 0.0 and 1.0 based on the given lower and upper bounds.
    """
    cdef double domain_diff = upper - lower
    if domain_diff == 0.0:
        return 0.0  # Avoid division by zero, return min_value
    return (value - lower) / domain_diff

def normalize_coordinates(double touch_x, double touch_y, double self_x, double self_y, double self_height,
                          double self_width):
    cdef (double, double) result = (0.0, 0.0)

    if self_width <= 0.0 or self_height <= 0.0:
        return result

    result[0] = CLAMP((touch_x - self_x) / self_width, 0.0, 1.0)
    result[1] = CLAMP((1.0 - (touch_y - self_y) / self_height), 0.0, 1.0)

    return result

def compute_ref_coords(double width, double height, double wX, double wY, double texture_width, double texture_height,
                       double span_x1, double span_y1, double span_x2, double span_y2,
                       double hl_pad_x, double hl_pad_y):
    """
    
    
        Since spans are computed relative to texture, we need to convert them to window coordinates

        Spans (x1, y1) references the top left corner of the text, a texture. 
        So x1 = 0, y1 = 0 means the top left corner of the texture.
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

    Parameters
    ----------
    width : float
        Widget width
    height : float
        Widget height
    wX : float
        Widget x position, in window coordinates
    wY : float
        Widget y position, in window coordinates
    texture_width : float
        Width of the rendered text texture
    texture_height : float
        Height of the rendered text texture
    span_x1, span_y1 : float
        Top-left corner of the ref bounding box, in texture coordinates
    span_x2, span_y2 : float
        Bottom-right corner of the ref bounding box, in texture coordinates
    hl_pad_x : float
        Horizontal highlight padding, extends the box beyond the text
    hl_pad_y : float
        Vertical highlight padding, extends the box beyond the text

    Returns
    -------
    tuple[float, float, float, float]
        (x1, y1, x2, y2) of the highlight box in window coordinates, y1 being the top edge

    """


    # X Coordinate
    # For X coordinate, we only need to consider the offset. The distance between the left edge of the widget and the text.
    
    cdef double offsetX = (width - texture_width) / 2.0
    span_x1 += offsetX
    span_x2 += offsetX

    
    # Y Coordinate
    # Spans are y-down from the texture top; the output is y-up from the widget bottom.
    # height - span_y - offsetY performs both steps at once: subtracting the centering offset
    # places the texture edge, and subtracting from height flips the axis.

    cdef double offsetY = (height - texture_height) / 2.0
    # After this flip, span_y1 is the top edge and span_y2 the bottom edge, y-up.
    span_y1 = height - span_y1 - offsetY
    span_y2 = height - span_y2 - offsetY

    # Highlight Padding
    # We want the highlight padding to extend outside of the span.
    # x: subtract from x1, add to x2.
    # y (y-up now): add to y1 (top edge), subtract from y2 (bottom edge).

    span_x1 -= hl_pad_x
    span_x2 += hl_pad_x
    span_y1 += hl_pad_y
    span_y2 -= hl_pad_y

    # Convert to window coordinates using the widget's position.
    span_x1 += wX
    span_x2 += wX
    span_y1 += wY
    span_y2 += wY

    return span_x1, span_y1, span_x2, span_y2

cdef inline double srgb_channel_to_linear(double c):
    return c / 12.92 if c <= 0.04045 else pow((c + 0.055) / 1.055, 2.4)

cdef double relative_luminance(double r, double g, double b):
    """WCAG relative luminance of an sRGB color, 0.0 (black) to 1.0 (white)"""
    return (0.2126 * srgb_channel_to_linear(r)
            + 0.7152 * srgb_channel_to_linear(g)
            + 0.0722 * srgb_channel_to_linear(b))

def compute_text_contrast(tuple background_color, tuple highlight_color = None):
    """
    Pick black or white text for a background.

    White text when the background's WCAG relative luminance is at most 0.179,
    the point where black and white text have equal contrast ratio
    (sqrt(1.05 * 0.05) - 0.05).

    Parameters
    ----------
    background_color : tuple[float, float, float, float]
        Background color of the widget, treated as opaque
    highlight_color : tuple[float, float, float, float], optional
        Highlight drawn over the background, composited using its alpha

    Returns
    -------
    str
        '#000000' or '#ffffff'
    """
    cdef double r = background_color[0]
    cdef double g = background_color[1]
    cdef double b = background_color[2]
    cdef double hl_a

    if highlight_color is not None:
        # Composite in gamma space, matching how the renderer blends the highlight
        hl_a = highlight_color[3]
        r = highlight_color[0] * hl_a + r * (1.0 - hl_a)
        g = highlight_color[1] * hl_a + g * (1.0 - hl_a)
        b = highlight_color[2] * hl_a + b * (1.0 - hl_a)

    if relative_luminance(r, g, b) > 0.179:
        return '#000000'
    return '#ffffff'


def compute_overscroll(double overscroll, double target_height, double overscroll_threshold):
    """
    Given our thresholds and target height, normalize the overscroll to a value between 0.0 and 1.0.
    """
    cdef double domain_height = target_height * overscroll_threshold
    return normalize_domain_range(CLAMP(abs(overscroll), 0, domain_height), 0.0, domain_height)