from pathlib import Path
from typing import Callable, Iterable

from toolz import curry
from toolz.curried import get, compose_left
from string import printable
import random
import pytest


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
def category_folders(
    tmpdir, img_maker
) -> Callable[[int], tuple[list[tuple[Path, Path]], Path]]:
    def _category_folders(n_categories) -> tuple[list[tuple[Path, Path]], Path]:
        expected = []
        for i in range(n_categories):
            cat_folder = Path(tmpdir) / str(i)
            cat_folder.mkdir()
            cat_img = img_maker(64, 64)
            cat_img.save(img_fp := (cat_folder / f"{i}.png"))
            expected.append((cat_folder, img_fp))
        return expected, Path(tmpdir)

    return _category_folders


@pytest.fixture()
def markdown_generator():
    """Spit out valid markdown"""

    def _markdown_generator():
        def random_line():
            return "".join(random.choices(printable, k=random.randint(1, 255)))

        while True:
            strategy = random.choice(("text", "code", "heading"))
            if strategy == "heading":
                yield ("#" * random.randint(1, 4)) + random_line()
                continue
            if strategy == "code":
                chunk = ["```python", random_line()]
                while random.randint(0, 1) < 1:
                    chunk.append(random_line())
                chunk.append("```")
                yield "\n".join(chunk)
                continue
            if strategy == "text":
                yield "\n".join((random_line() for i in range(random.randint(1, 5))))
                continue

    return _markdown_generator


@pytest.fixture
def filesystem_data(
    category_folders, markdown_generator
) -> Callable[[int, int], tuple[dict[Path, list[Path]], Path]]:
    def _filesystem_data(n_categories, n_notes) -> tuple[dict[Path, list[Path]], Path]:
        folders, parent = category_folders(n_categories)
        gen = markdown_generator()
        category_files = {}
        for category_folder, _ in folders:
            category_files[category_folder] = []
            for i in range(n_notes):
                note_path = category_folder / f"{i}.md"
                note_path.write_text(next(gen))
                category_files[category_folder].append(note_path)

        return category_files, parent

    return _filesystem_data
