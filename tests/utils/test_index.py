from contextlib import nullcontext as does_not_raise
from functools import partial

import pytest

from mindref.lib.ext import RollingIndex


@pytest.fixture
def gen_index(request):
    n_items, current_item, op = request.param
    idx = RollingIndex(size=n_items, current=current_item)

    def _cond(given, expected):
        with does_not_raise():
            assert given == expected

    if op == "next":
        if current_item == n_items - 1:
            cond = partial(_cond, expected=0)
        else:
            cond = partial(_cond, expected=current_item + 1)

    elif op == "previous":
        if current_item == 0:
            cond = partial(_cond, expected=n_items - 1)
        else:
            cond = partial(_cond, expected=current_item - 1)
    else:
        raise AssertionError(f"Unknown op {op}")

    return idx, cond, op


@pytest.mark.parametrize(
    "gen_index",
    [
        (1, 0, "next"),
        (1, 0, "previous"),
        (2, 0, "next"),
        (2, 0, "previous"),
        (2, 1, "previous"),
        (2, 1, "next"),
        (10, 9, "previous"),
        (10, 9, "next"),
    ],
    indirect=True,
)
def test_backend_index(gen_index):
    idx, cond, op = gen_index
    f = getattr(idx, op)
    f()
    cond(idx.current)


@pytest.mark.parametrize("direction", ["next", "previous"])
def test_index_peek(direction):
    """Test that peeking index does not change current"""

    idx = RollingIndex(size=10, current=5)
    f = getattr(idx, direction)
    f(peek=True)
    assert idx.current == 5
