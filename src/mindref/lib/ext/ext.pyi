def normalize_coordinates(
    touch_x: float,
    touch_y: float,
    self_x: float,
    self_y: float,
    self_height: float,
    self_width: float,
) -> tuple[float, float]: ...
def compute_ref_coords(
    width: float,
    height: float,
    wX: float,
    wY: float,
    texture_width: float,
    texture_height: float,
    span_x1: float,
    span_y1: float,
    span_x2: float,
    span_y2: float,
    hl_pad_x: float,
    hl_pad_y: float,
) -> tuple[float, float, float, float]: ...
def color_str_components(color_str: str) -> tuple[float, float, float, float]: ...
def compute_text_contrast(
    background_color: tuple[float, float, float, float],
    threshold: float,
    highlight_color: tuple[float, float, float, float] | None = None,
) -> str: ...
def compute_overscroll(
    overscroll: float,
    target_height: float,
    overscroll_threshold: float,
) -> float: ...
