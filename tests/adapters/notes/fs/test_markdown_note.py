from __future__ import annotations

from pathlib import Path

import pytest

from lib.domain.markdown_note import MarkdownNote


@pytest.fixture
def md_files(request, get_expected):
    fp = request.param
    return get_expected(fp)


def pytest_generate_tests(metafunc):
    if "md_files" in metafunc.fixturenames:
        md_files = (Path(__file__).parent / "data").glob("*.md")
        idlist, argvalues = [], []
        for md_file in md_files:
            idlist.append(md_file.name)
            argvalues.append(md_file)
        metafunc.parametrize("md_files", argvalues, ids=idlist, indirect=True)


def test_markdown_note(md_files):
    md_file_doc, conditions = md_files
    doc = MarkdownNote.from_file(category="test", idx=0, fp=md_file_doc)
    for cond in conditions:
        cond(doc)
