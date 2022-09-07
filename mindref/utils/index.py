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

    def next(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == self.end:
            self.current = 0
            return self.current
        else:
            self.current += 1
            return self.current

    def previous(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == 0:
            self.current = self.end
            return self.current
        else:
            self.current -= 1
            return self.current
