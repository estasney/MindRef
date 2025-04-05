# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "colour-science[optional]", "numpy"]
#
# ///
import click
import numpy as np
import colour


def hex_to_rgb01(h):
    return [int(h[i : i + 2], 16) / 255.0 for i in (1, 3, 5)]


def rgb01_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(round(c * 255) for c in rgb))


def perceptual_grayscale_steps_lab(start_hex, end_hex, steps=9):
    # Convert hex to RGB in 0-1 range
    start_rgb = np.array(hex_to_rgb01(start_hex))
    end_rgb = np.array(hex_to_rgb01(end_hex))

    # Convert from sRGB to Lab
    start_lab = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(start_rgb))
    end_lab = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(end_rgb))

    results = []
    for t in np.linspace(0, 1, steps):
        interp_lab = start_lab * (1 - t) + end_lab * t
        interp_xyz = colour.Lab_to_XYZ(interp_lab)
        interp_rgb = colour.XYZ_to_sRGB(interp_xyz)

        # Clip RGB to valid range
        interp_rgb = np.clip(interp_rgb, 0, 1)
        results.append(rgb01_to_hex(interp_rgb))

    return results


@click.command("color_gradient")
@click.option(
    "-s",
    "--start",
    type=click.STRING,
    prompt="Hex Start Color",
    help="Hex Start Color",
    default="#f5f5f5",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    prompt="Hex End Color",
    help="Hex End Color",
    default="#212121",
)
@click.option(
    "-n",
    "--steps",
    type=click.INT,
    prompt="Number of Steps",
    help="Number of Steps",
    default=10,
)
def color_gradient(start, end, steps):
    scaled_colors = perceptual_grayscale_steps_lab(start, end, steps)
    click.echo("\n".join(scaled_colors))


if __name__ == "__main__":
    color_gradient()  # pylint: disable=no-value-for-parameter
