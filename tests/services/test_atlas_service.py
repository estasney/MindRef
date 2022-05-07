import json

from kvnoteafly.services.atlas.atlas import AtlasService


def test_atlas_discovery(stored_atlas):
    atlas_folder = stored_atlas("test_atlas", *["a", "b", "c"])
    assert atlas_folder.exists()
    atlas_file = (atlas_folder / "test_atlas").with_suffix(".atlas")
    assert atlas_file.exists()
    with atlas_file.open(mode="r", encoding="utf-8") as fp:
        contents = json.load(fp)
    img_names = set(
        item for sublist in [v.keys() for v in contents.values()] for item in sublist
    )
    assert img_names == {"a", "b", "c"}
    service = AtlasService(storage_path=atlas_folder.parent)
    assert atlas_file in [atlas.path for atlas in service.atlases]
    for img in ["a", "b", "c"]:
        assert (
            service.uri_for(img, "test_atlas")
            == f"atlas://{atlas_file.with_suffix('')}/{img}"
        )
