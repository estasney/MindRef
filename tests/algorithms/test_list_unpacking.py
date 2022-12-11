from functools import partial
from itertools import product

import pytest
from toolz import get_in

from widgets.markdown.markdown_widget_parser import MarkdownWidgetParser

report = MarkdownWidgetParser._report_nested_lists  # noqa


def generate_dictionaries(nesting_level, num_children):
    """

    Parameters
    ----------
    nesting_level : Number of levels deep. 0 means a list with direct list_items
    num_children

    Returns
    -------

    """

    def item_factory(i_type):
        return {"type": i_type, "children": []}

    def block_text_factory(key):
        block = item_factory("block_text")
        block["children"].append({"type": "text", "text": key})
        return block

    def list_item_factory(l: int):
        item = item_factory("list_item")
        item |= {"level": l}
        return item

    list_factory = partial(item_factory, "list")

    # Create the base list dictionary
    d = list_factory()
    expected = list_factory()

    # Add direct, list_item children

    # At this point, d and expected are equal, but separate objects
    # Now, to add nesting
    # One level of nesting means we nest a list in a list_item. And then nest another list_item in the list.

    # Cursor starts with the first list_item's children

    def last_add_idx(cur, obj):
        return len(get_in(cur, obj, no_default=True)) - 1

    cursor = []
    for i in range(num_children):
        # Add direct, list_item children
        cursor.append("children")
        get_in(cursor, d, no_default=True).append(list_item_factory(i + 1))
        get_in(cursor, expected, no_default=True).append(list_item_factory(i + 1))

        # Add a block text to list_item
        cursor.extend((i, "children"))
        get_in(cursor, d, no_default=True).append(
            block_text_factory(f"Level 0, Child {i}")
        )
        get_in(cursor, expected, no_default=True).append(
            block_text_factory(f"Level 0, Child {i}")
        )
        cursor.clear()
        for level in range(nesting_level):
            cursor_e = ["children"]
            # list -> i > list_item > children at level 0
            # list -> i > list_item > children > 0 > children at level 1
            cursor_d = ["children", i, "children"] + [1, "children"] * level

            # add the nested list

            get_in(cursor_d, d, no_default=True).append(list_factory())
            # no equivalent action for expected
            # get index of the list we just added
            cursor_d.append(last_add_idx(cursor_d, d))
            # select its children
            cursor_d.append("children")

            # list_item
            # =========

            # add the nested list_item
            get_in(cursor_d, d, no_default=True).append(list_item_factory(level + 2))
            # get the index of list_item
            cursor_d.append(last_add_idx(cursor_d, d))
            # select its children
            cursor_d.append("children")

            # append the list_item to expected
            get_in(cursor_e, expected, no_default=True).append(
                list_item_factory(level + 2)
            )
            # get the index of what we just added
            cursor_e.append(last_add_idx(cursor_e, expected))
            # select its children
            cursor_e.append("children")

            # text_block
            # ==========

            # add the nested text_block to d
            get_in(cursor_d, d, no_default=True).append(
                block_text_factory(f"Level {level + 2}")
            )

            # add the text_block to expected

            get_in(cursor_e, expected, no_default=True).append(
                block_text_factory(f"Level {level + 2}")
            )

    return d, expected


def dictionary_params():
    nest_level = range(1, 6)
    n_children = range(1, 5)
    params = product(nest_level, n_children)
    for level, n_child in params:
        given, expected = generate_dictionaries(level, n_child)
        param_id = f"L:[{level}],C:[{n_child}]"
        yield pytest.param((given, expected, level, n_child), id=param_id)


def extract(x, idx):
    return get_in(idx, x), idx


@pytest.mark.parametrize("variant", dictionary_params())
def test_variant_generation(variant):
    given, expected, nest_level, n_children = variant
    assert given["type"] == "list"
    assert isinstance(given["children"], list)

    assert expected["type"] == "list"
    assert isinstance(expected["children"], list)

    cursor_d = ["children"]
    for i in range(n_children):
        cursor_d.append(i)
        assert get_in(cursor_d, given) is not None
        cursor_d.pop()


def matching_keys(expected: dict, result: dict):
    return not bool(set(expected.keys()) ^ set(result.keys()))


def matches_first_level(expected: dict, result: dict):
    expected_children = expected["children"]
    result_children = [
        r
        for r in result["children"]
        if "type" in r and r["type"] not in {"list", "list_item"}
    ]
    for ec, rc in zip(expected_children, result_children):
        assert ec == rc
    return True


@pytest.mark.parametrize("variant", dictionary_params())
def test_list_unpacking(variant):
    given, expected, nest_level, n_children = variant

    result = {"type": "list", "children": []}
    reports = report(
        given,
        None,
        {
            "list_item",
        },
    )
    for r in reports:
        child_data = get_in(r, given)
        result["children"].append(child_data)

    assert matching_keys(expected, result)
    expected_children = expected["children"]
    result_children = result["children"]
    assert len(expected_children) == len(
        result_children
    ), "Different number of children"
    for expected_child, result_child in zip(expected_children, result_children):
        assert matching_keys(expected_child, result_child)
        assert matches_first_level(expected_child, result_child)
