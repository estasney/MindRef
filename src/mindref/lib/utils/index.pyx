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
