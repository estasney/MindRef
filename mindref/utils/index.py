from __future__ import annotations


class RollingIndex:
    """
    Implements rolling index so that we can always call `next` or `previous`

    As with `range`, `end` is not inclusive
    """

    def __init__(self, size: int, current=0):
        self.size = size
        self.start = 0
        self.end = max([0, (size - 1)])
        self.current = current

    def set_current(self, n: int):
        if n >= self.size:
            raise IndexError(f"{n} is greater the {self.size}")
        self.current = n

    def next(self, peek=False) -> int:
        """
        Get the next value
        Parameters
        ----------
        peek : bool
            If True, don't advance the index

        Returns
        -------
        """
        next_index = self.current + 1
        if next_index > self.end:
            next_index = 0
        if peek:
            return next_index
        self.current = next_index
        return self.current

    def previous(self, peek=False) -> int:
        """
        Get the previous value
        Parameters
        ----------
        peek : bool
            If True, don't move the index

        Returns
        -------

        """
        prev_index = self.current - 1
        if prev_index < 0:
            prev_index = self.end
        if peek:
            return prev_index
        self.current = prev_index
        return self.current
