from pathlib import Path
from typing import Iterable

from toolz import curry
from toolz.curried import get, nth, compose_left
import pytest


def pytest_generate_tests(metafunc):
    if "md_files" in metafunc.fixturenames:
        md_files = (Path(__file__).parent.parent / "data").glob("*.md")
        idlist, argvalues = [], []
        for md_file in md_files:
            idlist.append(md_file.name)
            argvalues.append(md_file)
        metafunc.parametrize("md_files", argvalues, ids=idlist, indirect=True)


def _get_expected(fp):
    def _has_table(doc):
        return any((item["type"] == "table" for item in doc))

    @curry
    def _get_table(n, doc):
        return list([item for item in doc if item["type"] == "table"])[n]

    def _has_block_code(doc):
        return any((item["type"] == "block_code" for item in doc))

    def _has_block_code_with_info(info, doc):
        return any(
            (item["type"] == "block_code" and item["info"] == info for item in doc)
        )

    def is_table_head(d):
        assert (
            d["type"] == "table_head"
        ), f"getter should have returned 'table_head', but returned {d}"
        return d

    @curry
    def _getattr(name, item):
        return getattr(item, name)

    _get_title = _getattr("title")
    _get_document = _getattr("document")
    _get_sk = _getattr("shortcut_keys")
    _get_text = _getattr("text")
    _get_table_head = compose_left(
        _get_document, _get_table(0), get("children"), get(0), is_table_head
    )

    @curry
    def has_aligned_table(alignments, doc):
        head = _get_table_head(doc)
        for i, child in enumerate(head["children"]):
            assert (
                child["type"] == "table_cell"
            ), f"getter should have returned 'table_head', but returned {child}"
            assert (
                child["align"] == alignments[i]
            ), f"Child has alignment {child['align']} but expected {alignments[i]}"

    @curry
    def has_title(title, item):
        val = _get_title(item)
        assert val == title, f"Title Should Be {title}"

    @curry
    def has_block_code(info, item):
        doc = _get_document(item)
        if info is None:
            assert _has_block_code(
                doc
            ), f"Document Should Have block_code with Info {info}"
        else:
            assert _has_block_code_with_info(
                info, doc
            ), f"Document Should Have Block_code with Info {info}"

    @curry
    def _having_text(val: bool, substr: Iterable[str], item):
        text = _get_text(item)
        for s in substr:
            assert (
                s in text
            ) is val, f"'{substr}' Should {'Not' if False else ''} Be In {text}"

    @curry
    def _having_table(val: bool, item):
        doc = _get_document(item)
        assert _has_table(doc) is val, f"Should {'Not' if False else ''} Have Table"

    @curry
    def _having_shortcut_keys(val: bool, item):
        keys = _get_sk(item)
        if val:
            assert keys is not None, f"Shortcut Keys Should Be Set"
        else:
            assert keys is None, f"Shortcut Keys Should Be None"

    has_table = _having_table(True)
    no_table = _having_table(False)
    has_sk_keys = _having_shortcut_keys(True)
    no_sk_keys = _having_shortcut_keys(False)
    has_text_with = _having_text(True)
    no_text_with = _having_text(False)

    data = {
        "Decorators.md": [
            no_table,
            has_title("Decorators"),
            has_block_code("python"),
            no_sk_keys,
        ],
        "Pattern Matching Operators.md": [
            has_table,
            has_title("Pattern Matching Operators"),
            has_aligned_table(["left", "center"]),
            no_sk_keys,
        ],
        "Accept suggestion.md": [
            no_table,
            has_title("Accept suggestion, with syntax fixing"),
            has_sk_keys,
            no_text_with(["shortcut", "Ctrl", "Enter", "Shift", "```"]),
        ],
        "Zen.md": [
            no_table,
            has_title("The Zen of Python, by Tim Peters"),
        ],
    }
    return fp, data[fp.name]


@pytest.fixture
def get_expected():
    return _get_expected


@pytest.fixture
def category_folders(tmpdir, img_maker):
    def _category_folders(n_categories):
        expected = []
        for i in range(n_categories):
            cat_folder = Path(tmpdir) / str(i)
            cat_folder.mkdir()
            cat_img = img_maker(64, 64)
            cat_img.save(f"{i}.png")
            expected.append((cat_folder, cat_img))
        return expected, Path(tmpdir)

    return _category_folders
