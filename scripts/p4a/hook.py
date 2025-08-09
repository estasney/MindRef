import re
from copy import copy
from pathlib import Path
from pathlib import Path
from xml.etree import ElementTree as ET


REPO_PATTERN = re.compile(r"(?<=repositories {)(?:[^}]+)(})")

FLATDIR_SNIPPET = 'flatDir { dirs "libs" }'


def _needs_flatdir(doc: str) -> bool:
    return "flatDir" not in doc


def patch(doc: str) -> str:
    # Reverse the matches
    # Each group(1)'s start pos is where the snippet should be inserted

    doc_head, doc_tail = "", ""
    doc_copy = copy(doc)

    for match in list(reversed(list(REPO_PATTERN.finditer(doc)))):
        doc_head = doc_copy[: match.start(1)]
        doc_tail = doc_copy[match.end(1) - 1 :]
        doc_copy = f"{doc_head}{FLATDIR_SNIPPET}\n{doc_tail}"

    return doc_copy


PROFILEABLE_TAG = {"{http://schemas.android.com/apk/res/android}shell": "true"}


def after_apk_build(ctx, **kwargs) -> None:
    """
    p4a hook: runs once the dist is ready but *before* gradle builds.
    Adds `flatDir { dirs "libs" }` to <dist>/build.gradle unless present.
    """
    gradle_path = Path(ctx._dist.dist_dir) / "build.gradle"
    if not gradle_path.exists():
        print(f"[after_build] build.gradle not found: {gradle_path}")
        return

    doc = gradle_path.read_text(encoding="utf-8")
    if not _needs_flatdir(doc):
        print("[after_build] flatDir already present – skipping patch.")
        return

    patched_doc = patch(doc)
    gradle_path.write_text(patched_doc, encoding="utf-8")

    manifest = Path(ctx._dist.dist_dir) / "src/main/AndroidManifest.xml"

    tree = ET.parse(manifest)
    app = tree.getroot().find("application")
    if app is None:
        raise RuntimeError("No <application> tag found in manifest")

    if app.find("profileable") is None:
        ET.SubElement(app, "profileable", PROFILEABLE_TAG)
        tree.write(manifest, encoding="utf-8", xml_declaration=True)
        print("✓ inserted <profileable/> into AndroidManifest.xml")
