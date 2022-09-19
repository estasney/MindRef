from bisect import bisect
from collections import deque

import pytest


@pytest.fixture
def deque_maker(request):
    n_items, maxlen, insert_val, expected = request.param
    deque_vals = list(range(n_items))
    d = deque(deque_vals, maxlen=maxlen)
    return d, insert_val, expected


def run_bisect(x, val, idx):
    if idx == 0:
        return list(x)
    if x.maxlen == len(x):
        x.popleft()
        idx -= 1
    if idx == 0:
        x.appendleft(val)
        return list(x)
    r = len(x) - idx
    x.rotate(r)
    x.append(val)
    x.rotate(-r)
    return list(x)


@pytest.mark.parametrize(
    "deque_maker",
    [
        (5, 3, 1, [2, 3, 4]),
        (5, 3, 5, [3, 4, 5]),
        (5, 3, 4, [3, 4, 4]),
        (5, 3, 2.5, [2.5, 3, 4]),
        (5, 4, 2.5, [2, 2.5, 3, 4]),
    ],
    indirect=True,
)
def test_deque_bisect(deque_maker):
    d, insert_val, expected = deque_maker
    keys = list(d)
    idx = bisect(keys, insert_val)
    result = run_bisect(d, insert_val, idx)
    assert result == expected
