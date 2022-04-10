import json
import os
from glob import glob
from pathlib import Path

import click
from PIL import Image


@click.option(
    "-i",
    "--image-glob",
    type=click.STRING,
    prompt=True,
    help="Glob pattern of images to pack",
)
@click.option(
    "-o", "--atlas-output", type=click.STRING, prompt=True, help="Path to save atlas"
)
@click.option("-p", "--padding", type=click.INT, default=2)
@click.option("-rm", "--remove", type=click.BOOL, default=False)
@click.command()
def make_atlas(image_glob, atlas_output, padding, remove):
    """Creates an atlas"""
    atlas_fp = Path(atlas_output)
    if not atlas_fp.suffix:
        atlas_fp = atlas_fp.with_suffix(".atlas")

    if atlas_fp.exists():
        with open(atlas_fp, "r", encoding="utf-8") as fp:
            atlas_file = json.load(fp)
            atlas_keys = list(atlas_file.keys())
        atlas_fp.unlink()
        for key_file in atlas_keys:
            (Path(atlas_fp.parent) / key_file).unlink(missing_ok=True)

    img_files = glob(image_glob)

    # detect max width and height
    # The atlas size must be at least this size
    max_w, max_h = padding, padding
    for f in img_files:
        with Image.open(f) as im:
            im_w, im_h = im.size
            im_w += padding
            im_h += padding
            max_w = max(im_w, max_w)
            max_h = max(im_h, max_h)

    atlas_size = max(max_w, max_h)
    os.environ["KIVY_NO_ARGS"] = "1"
    from kivy.atlas import Atlas

    Atlas.create(str(atlas_fp.with_suffix("")), img_files, atlas_size)
    if remove:
        for f in img_files:
            click.echo(f"Removing {f}")
            os.unlink(f)


if __name__ == "__main__":
    make_atlas()
