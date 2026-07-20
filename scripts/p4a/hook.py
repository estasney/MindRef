import re
from copy import copy
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


ANDROID_NAMESPACE = "http://schemas.android.com/apk/res/android"

PROFILEABLE_TAG = {f"{{{ANDROID_NAMESPACE}}}shell": "true"}

# Without this, rewriting the manifest renames the `android` prefix to `ns0`.
# The manifest merger then fails to reconcile it against library manifests,
# which declare their attributes against the `android` prefix.
ET.register_namespace("android", ANDROID_NAMESPACE)


def write_splash_theme_override(dist_dir: Path) -> None:
    """
    The launcher activity uses the generated KivySupportCutout style, which
    API 31+ also consults for the system splash screen; without an override
    the splash background falls back to white. A same-named style in
    values-v31 replaces the base wholesale, so copy the generated style and
    append the splash background color (matches the adaptive icon background).
    """
    res_dir = dist_dir / "src/main/res"
    strings = ET.parse(res_dir / "values/strings.xml")
    style = strings.getroot().find("style[@name='KivySupportCutout']")
    if style is None:
        raise RuntimeError("KivySupportCutout style not found in strings.xml")

    item = ET.SubElement(
        style, "item", {"name": "android:windowSplashScreenBackground"}
    )
    item.text = "#FF37464F"

    resources = ET.Element("resources")
    resources.append(style)
    values_v31 = res_dir / "values-v31"
    values_v31.mkdir(exist_ok=True)
    ET.ElementTree(resources).write(
        values_v31 / "themes.xml", encoding="utf-8", xml_declaration=True
    )
    print("[after_build] wrote values-v31 KivySupportCutout splash override")


def after_apk_build(ctx, **kwargs) -> None:
    """
    p4a hook: runs once the dist is ready but *before* gradle builds.
    Adds `flatDir { dirs "libs" }` to <dist>/build.gradle unless present.
    """
    dist_dir = Path(ctx._dist.dist_dir)
    write_splash_theme_override(dist_dir)

    gradle_path = dist_dir / "build.gradle"
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
        print("[after_build] inserted <profileable/> into AndroidManifest.xml")
