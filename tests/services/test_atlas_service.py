import json

import pytest

from kvnoteafly.services.atlas.atlas import AtlasService


@pytest.mark.parametrize("atlas_type", ["mono", "multi"])
@pytest.mark.parametrize("n", [1, 5, 20])
def test_atlas_discovery(stored_atlas, atlas_type, n):

    """
    Given atlas file, folder and images
    Check that Atlas Service identifies them and provides uri's correctly
    """
    atlas_folder, image_names = stored_atlas("test_atlas", atlas_type, n)
    assert atlas_folder.exists()
    atlas_file = (atlas_folder / "test_atlas").with_suffix(".atlas")
    assert atlas_file.exists()
    with atlas_file.open(mode="r", encoding="utf-8") as fp:
        contents = json.load(fp)
    service = AtlasService(storage_path=atlas_folder.parent)
    assert atlas_file in [atlas.path for atlas in service.atlases]
    for img in image_names:
        assert (
            service.uri_for(img, "test_atlas")
            == f"atlas://{atlas_file.with_suffix('')}/{img}"
        )
