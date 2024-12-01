cdef class RollingIndex:
    cdef int _size
    cdef int _start
    cdef int _end
    cdef int _current

    cdef bint _set_current(self, int n)
    cdef int _next(self, bint peek)
    cdef int _prev(self, bint peek)
