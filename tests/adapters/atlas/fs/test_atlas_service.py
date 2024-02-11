import atexit
import json
import random
import string
from pathlib import Path

import pytest

from lib.adapters.atlas.fs.fs_atlas_repository import AtlasService


@pytest.mark.parametrize("atlas_type", ["mono", "multi"])
@pytest.mark.parametrize("n", [1, 5, 20])
@pytest.mark.atlas
def test_atlas_discovery(stored_atlas, atlas_type, n):
    """
    Given atlas file, folder and images
    Check that Atlas Service identifies them and provides uri's correctly
    """
    atlas_folder, image_names = stored_atlas("test_atlas", atlas_type, n)
    assert atlas_folder.exists()
    atlas_file = (atlas_folder / "test_atlas").with_suffix(".atlas")
    assert atlas_file.exists()

    service = AtlasService(storage_path=atlas_folder.parent)
    assert atlas_file in [atlas.path for atlas in service.atlases]
    for img in image_names:
        assert (
            service.uri_for(img, "test_atlas")
            == f"atlas://{atlas_file.with_suffix('')}/{img}"
        )


@pytest.mark.parametrize("duplicated", [True, False])
@pytest.mark.parametrize("atlas_type", ["mono", "multi"])
@pytest.mark.parametrize("n", [1, 5, 20])
@pytest.mark.atlas
def test_append_atlas(stored_atlas, atlas_type, n, img_name, duplicated, img_maker):
    atlas_folder, image_names = stored_atlas("test_atlas", atlas_type, n)
    atlas_file = (atlas_folder / "test_atlas").with_suffix(".atlas")
    service = AtlasService(storage_path=atlas_folder.parent)
    assert atlas_file in [atlas.path for atlas in service.atlases]

    # Ensure image names are included
    for img in image_names:
        assert (
            service.uri_for(img, "test_atlas")
            == f"atlas://{atlas_file.with_suffix('')}/{img}"
        )

    atlas_folder_contents = set(atlas_folder.iterdir())

    # Make a new image
    app_img = img_maker(100, 100)
    # Random name or a duplicated one
    app_img_name = (
        img_name(string.ascii_lowercase, (1, 16))
        if not duplicated
        else random.choice(image_names)
    )
    from tempfile import TemporaryDirectory

    app_fp_dir = TemporaryDirectory()
    atexit.register(lambda: app_fp_dir.cleanup())
    app_img_fp = (Path(app_fp_dir.name) / app_img_name).with_suffix(".png")
    app_img.save(app_img_fp)

    # Test the service

    if duplicated:
        with pytest.raises(KeyError):
            service.save_to_atlas(
                [app_img_fp],
                [app_img_name],
                atlas_name="test_atlas",
                atlas_size=(512, 512),
            ), "Duplicate not caught"
        return

    service.save_to_atlas(
        [app_img_fp], [app_img_name], atlas_name="test_atlas", atlas_size=(512, 512)
    )

    # Test that existing images are still included in atlas
    for img in image_names:
        assert (
            service.uri_for(img, "test_atlas")
            == f"atlas://{atlas_file.with_suffix('')}/{img}"
        )

    # Test that each atlas image exists
    d = json.loads(atlas_file.read_text())
    for atlas_img_key in d.keys():
        assert (atlas_folder / atlas_img_key).exists()

    assert (
        service.uri_for(app_img_name, "test_atlas")
        == f"atlas://{atlas_file.with_suffix('')}/{app_img_name}"
    )
    assert set(atlas_folder.iterdir()).issuperset(atlas_folder_contents)
