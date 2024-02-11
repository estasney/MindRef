# cython: language_level=3, cdivision=True
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
