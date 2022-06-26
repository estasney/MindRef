import pytest
from contextlib import nullcontext as does_not_raise
from adapters.notes.note_repository import NoteIndex
from functools import partial


@pytest.fixture
def gen_index(request):
    n_items, current_item = request.param
    idx_next = NoteIndex(size=n_items, current=current_item)
    idx_prev = NoteIndex(size=n_items, current=current_item)

    def _cond(given, expected):
        with does_not_raise():
            assert given == expected

    if current_item + 1 == n_items:
        cond_next = partial(_cond, expected=0)
    else:
        cond_next = partial(_cond, expected=current_item + 1)

    if current_item == 0:
        cond_prev = partial(_cond, expected=n_items - 1)
    else:
        cond_prev = partial(_cond, expected=current_item - 1)

    return idx_next, cond_next, idx_prev, cond_prev


@pytest.mark.parametrize("gen_index", [(1, 0), (2, 0), (2, 1), (10, 9)], indirect=True)
def test_backend_index(gen_index):
    idx_next, cond_next, idx_prev, cond_prev = gen_index
    idx_next.next()
    cond_next(idx_next.current)
    idx_prev.previous()
    cond_prev(idx_prev.current)
