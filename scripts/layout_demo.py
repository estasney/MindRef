from pathlib import Path
from typing import Optional
from itertools import chain
import mistune
from kivy.core.text import Label, LabelBase
from kivy.core.text.text_layout import layout_text
from collections import namedtuple

text = Path("/nfs/kvnotes/Git/Merge vs Rebase.md").read_text()
md = mistune.create_markdown(renderer=mistune.AstRenderer(), plugins=["table"])
md_doc = md(text)

TextSnippet = namedtuple("TextSnippet", "text, highlight")
TextSnippetLayout = namedtuple(
    "TextSnippetLayout", "text, highlight, pos_x, w, pos_y, h"
)

BOLD = "1"
BG_YELLOW = "43"
END = "\033[0m"


def filter_inline_child(n):
    if len(n["children"]) <= 1:
        return False
    if any((c["type"] == "codespan") for c in n["children"]):
        return True
    return False


def make_snippet(x):
    snippets = []
    last_child = len(x["children"]) - 1
    for i, c in enumerate(x["children"]):
        if i == last_child:
            snippets.append(
                TextSnippet(c["text"] + "\n", highlight=c["type"] == "codespan")
            )
        else:
            snippets.append(TextSnippet(c["text"], highlight=c["type"] == "codespan"))
    return snippets


doc = filter(filter_inline_child, md_doc)
doc = map(make_snippet, doc)
doc = list(chain.from_iterable(doc))


def tokenize(texts: list[TextSnippet]):
    for t in texts:
        yield t.text, t.highlight


def run_layout(
    snippets: list[TextSnippet], max_width: Optional[int], max_height: Optional[int]
):
    l = Label()
    lines = []
    get_extents = l.get_cached_extents()
    space_width, _ = get_extents(" ")
    l_opt_default = {**l.options, **{"space_width": space_width, "font_name": "Roboto"}}
    l_opt_mono = {
        **l.options,
        **{"space_width": space_width, "font_name": "RobotoMono"},
    }

    current_w, current_h = 0, 0
    for t, hl in tokenize(snippets):
        opt = l_opt_default if not hl else l_opt_mono
        current_w, current_h, clipped = layout_text(
            t,
            lines,
            (current_w, current_h),
            (max_width, max_height),
            opt,
            get_extents,
            True,
            False,
        )

    current_w, current_h, _ = layout_text(
        "",
        lines,
        (current_w, current_h),
        (max_width, max_height),
        l_opt_default,
        get_extents,
        True,
        True,
    )

    for i, line in enumerate(lines):
        for word in line.words:
            word_token = word.text
            word_hl = word.options["font_name"] == "RobotoMono"
            if word_hl:
                print("\033[" + BG_YELLOW + ";" + BOLD + "m" + word.text + END, end="")
            else:
                print(word.text, end="")
        print()


if __name__ == "__main__":
    LabelBase.register(
        name="RobotoMono",
        fn_regular=str(
            Path(__file__).parent.parent
            / "mindref"
            / "assets"
            / "RobotoMono-Regular.ttf"
        ),
    )
    run_layout(doc, max_width=500, max_height=None)
