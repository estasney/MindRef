import re
import click


@click.command("get_color_from_hex")
@click.option(
    "-c",
    "--color",
    type=click.STRING,
    prompt="Hex Color",
    help="Hex Code",
    default="#ffffff",
)
def get_color_from_hex(color: str = "#ffffff"):
    """
    CLI to Convert Hex Color's into 0-1 tuples
    Copied from Kivy
    """

    color = color.removeprefix("#")

    value = [
        int(x, 16) / 255.0 for x in re.split(r"([\da-f]{2})", color.lower()) if x != ""
    ]
    if len(value) == 3:
        value.append(1.0)
    click.echo(tuple(value))


if __name__ == "__main__":
    get_color_from_hex()
