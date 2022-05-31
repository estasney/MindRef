from glob import glob
from pathlib import Path
from typing import Optional

import click


@click.group("atlas_cli")
def atlas_cli():
    ...


@atlas_cli.command("pack")
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
@click.option("-s", "--size", type=click.STRING, default=None)
def make_atlas(image_glob, atlas_output, padding, remove, size: Optional[str] = None):
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
    if not size:
        max_w, max_h = padding, padding
        for f in img_files:
            with Image.open(f) as im:
                im_w, im_h = im.size
                im_w += padding
                im_h += padding
                max_w = max(im_w, max_w)
                max_h = max(im_h, max_h)

        atlas_size = max(max_w, max_h)
        atlas_size *= 6
    else:
        size = size.lower().replace("x", ",").split(",")
        if len(size) == 1:
            atlas_size = (int(size[0]), int(size[0]))
        else:
            atlas_size = (int(size[0]), int(size[1]))
    os.environ["KIVY_NO_ARGS"] = "1"
    from kivy.atlas import Atlas

    Atlas.create(str(atlas_fp.with_suffix("")), img_files, atlas_size)
    if remove:
        for f in img_files:
            click.echo(f"Removing {f}")
            os.unlink(f)


import json
import os
from collections import namedtuple
from typing import Tuple, Dict

import click
from PIL import Image

CropC = namedtuple("CropC", "x, y, w, h")


def cropbox(coords, im):
    x, y, w, h = coords

    x1 = x
    y1 = im.height - h - y
    w1 = x1 + w
    h1 = y1 + h

    return CropC(x1, y1, w1, h1)


def unpack_atlas_imgs(
    img_fp: str, imgs: Dict[str, Tuple[int, int, int, int]], output_dir: str
):
    im = Image.open(img_fp)
    _, img_ext = os.path.splitext(img_fp)
    for img_name, img_coords in imgs.items():
        cc = cropbox(img_coords, im)
        cropped_im = im.crop((cc.x, cc.y, cc.w, cc.h))
        cropped_im_fp = os.path.join(output_dir, f"{img_name}{img_ext}")
        cropped_im.save(cropped_im_fp, format="png")


@atlas_cli.command("unpack")
@click.argument("atlas_fp", type=click.Path(exists=True))
def unpack_atlas(atlas_fp):
    """Unpacks an atlas"""
    if not atlas_fp.endswith(".atlas"):
        raise ValueError(f"Expected Atlas File, Received {atlas_fp}")
    click.echo("Unpacking atlas")
    with open(atlas_fp, "r") as fp:
        atlas_data = json.load(fp)

    atlas_dir, _ = os.path.split(atlas_fp)
    for atlas_img, imgs in atlas_data.items():
        atlas_img_fp = os.path.join(atlas_dir, atlas_img)
        print(atlas_img_fp)
        print(imgs)
        unpack_atlas_imgs(atlas_img_fp, imgs, atlas_dir)


if __name__ == "__main__":
    atlas_cli()
