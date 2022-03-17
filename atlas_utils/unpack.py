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


def unpack_atlas_imgs(img_fp: str, imgs: Dict[str, Tuple[int, int, int, int]], output_dir: str):
    im = Image.open(img_fp)
    _, img_ext = os.path.splitext(img_fp)
    for img_name, img_coords in imgs.items():
        cc = cropbox(img_coords, im)
        cropped_im = im.crop((cc.x, cc.y, cc.w, cc.h))
        cropped_im_fp = os.path.join(output_dir, f"{img_name}{img_ext}")
        cropped_im.save(cropped_im_fp, format="png")


@click.command()
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


if __name__ == '__main__':
    unpack_atlas()
