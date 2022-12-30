# cython: language_level=3, cdivision=True

def normalize_coordinates(float touch_x, float touch_y, float self_x, float self_y,
                          float self_height, float self_width):
    cdef float x_local, y_local

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
