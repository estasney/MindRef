from __future__ import annotations

import pytest

from domain.markdown_note import MarkdownNote


@pytest.fixture
def md_files(request, get_expected):
    fp = request.param
    return get_expected(fp)


def test_markdown_note(md_files):
    md_file_doc, conditions = md_files
    doc = MarkdownNote.from_file(category="test", idx=0, fp=md_file_doc)
    for cond in conditions:
        cond(doc)
