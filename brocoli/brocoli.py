#!/usr/bin/env python3

import logging

import click
import yaml

from .TheFractalBot import bot
from .fractal import Fractal
from .processing import SimpleCamera, Coloration
from .processing.colors import hex2rgb
from .processing.compute import timeit

yaml.add_representer(
    Coloration, lambda dumper, data: dumper.represent_scalar("!kind", data.value)
)
yaml.add_constructor(
    "!kind", lambda loader, node: Coloration(loader.construct_scalar(node))
)

logger = logging.getLogger("brocoli")


def save(pil_image, click_file):
    """Save the image to the file and prints where it is saved. Handles stdout."""

    if "." in click_file.name:
        pil_image.save(click_file)
        logger.info(f"Saved as {click_file.name}")
    else:
        # if stdout is passed as file
        pil_image.save(click_file, "jpeg")


# ---- Definitions of click ParamTypes form argument parsing ---- #


def click_type(t_name, hint=""):
    """Transform a function to convert a str into a given type to a click ParamType instance."""

    def decorator(f):
        class Type(click.ParamType):
            name = t_name

            def convert(self, value, param=None, ctx=None):
                try:
                    return f(value)
                except (ValueError, TypeError, KeyError):
                    self.fail(
                        f"{value!r} is not a valid {self.name}. {hint}", param, ctx,
                    )

        return Type()

    return decorator


@click_type("size")
def size_type(val: str):
    named = {
        "4K": (3840, 2160),
        "FHD": (1920, 1080),
        "FULLHD": (1920, 1080),
        "1080P": (1920, 1080),
        "720P": (1280, 720),
        "QHD": (2560, 1440),
    }

    if val.upper() in named:
        return named[val.upper()]

    w, _, h = val.partition("x")
    return int(w), int(h)


complex_type = click_type("complex")(complex)
color_type = click_type(
    "color", hint="Must be in hexadecimal format or a common english name"
)(hex2rgb)


@click_type("coloration kind", hint="Coloration must be one of [C|A|T|S|I]")
def enum_type(val):
    d = {
        "a": Coloration.ANGLE,
        "t": Coloration.TIME,
        "s": Coloration.SMOOTH_TIME,
        "i": Coloration.AVG_TRIANGLE_INEQUALITY,
        "c": Coloration.AVG_CURVATURE,
    }

    return d[val.lower()]


@click_type("gradient", hint="A gradient must be hex colors separated by dashes.")
def gradient_type(val: str):
    if val.endswith("-"):
        val += val.partition("-")[0]
    colors = [hex2rgb(c) for c in val.split("-")]
    return colors


output_file_option = click.option(
    "--output-file",
    "-o",
    default="output.png",
    type=click.File("wb"),
    help="File to save the fractal. Pass - for stdout.",
)


def setup_logging(ctx, param, level):
    if ctx.resilient_parsing:
        return

    logger = logging.getLogger("brocoli")

    if logger.level == logging.NOTSET:
        logger.setLevel(logging.WARNING)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

    level = [logging.WARNING, logging.INFO, 15, logging.DEBUG][min(level, 3)]

    logger.setLevel(min(logger.level, level))


verbose_option = click.option(
    "--verbose",
    "-v",
    count=True,
    callback=setup_logging,
    expose_value=False,
    help="Log level -v to -vvv can be passed.",
)

# ---- Definition of the command line interface ---- #


@click.group()
@verbose_option
def cli():
    """A fractal generation tool by @ddorn."""


@cli.command()
def gui():
    """Start Brocoli's GUI."""

    try:
        from .kivymain import BrocoliApp
    except ImportError:
        click.secho("The GUI need kivy and kivymd to run.", fg="red")
        click.secho("Please install them via pip.")
        click.secho("   pip install -U --user kivy kivymd")
        quit(1)
    else:
        BrocoliApp().run()


@cli.command()
@click.argument("size", type=size_type, default="1920x1080")
@click.option("--show", "-s", is_flag=True)
@click.option("--yaml", "-y", "yaml_file", type=click.File("w",))
@output_file_option
@verbose_option
def random(size, show, output_file, yaml_file):
    """Generate a random fractal of a given SIZE."""

    from .processing.random_fractal import random_fractal
    from PIL import Image

    fractal = random_fractal(size)

    with timeit("Rendering"):
        surf = fractal.render()

    image = Image.fromarray(surf, mode="RGB")

    if output_file.name == "<stdout>":
        # if stdout is passed as output_file
        image.save(output_file, "jpeg")
    else:
        image.save(output_file)

    if yaml_file:
        yaml.dump(fractal, yaml_file)

    if show:
        image.show()


@cli.command()
@click.argument("center", type=complex_type, default=-0.75 + 0j)
@click.option("--size", "-x", type=size_type, default="1920x1080")
@click.option("--zoom", "-z", default=1, help="Complex height is 3/2**zoom.")
@click.option("--kind", "-k", type=enum_type, default="S")
@click.option("--limit", "-l", default=256, help="Max number of steps for each point.")
@click.option("--bound", "-b", default=200_000, help="Escape Module.")
@click.option("--julia", "-j", type=complex_type, help="Julia seed.")
@click.option(
    "--normalize-quantiles", "-q", is_flag=True, help="Colors has the same area."
)
@click.option("--steps-power", "-p", default=1.0, help="Enhance low or high values.")
@click.option(
    "--gradient-points",
    "-g",
    type=gradient_type,
    default=("0F4152-59A07B-F7E491-EDB825-EB3615"),
    help="Dash separeted hex colors. A trailing dash loops the gradient.",
)
@click.option("--color-count", "-c", default=256, help="Steps in the gradient.")
@click.option("--gradient-speed", "-s", default=1.0, help="Gradient speed.")
@click.option("--gradient-offset", "-S", default=0.0, help="Gradient offset.")
@click.option("--inside-color", "-i", type=color_type, help="Gradient offset.")
@click.option("--dry", "-d", is_flag=True, help="Print the fractal. Don't compute.")
@click.option(
    "--yaml",
    "yaml_file",
    type=click.File(),
    help="Get parameters from a yaml file instead.",
)
@output_file_option
def gen(dry, output_file, yaml_file, **kwargs):
    """Generate a fractal image with a lot of parameters."""

    if yaml_file:
        fractal = yaml.full_load(yaml_file)
    else:
        size = kwargs.pop("size")
        center = kwargs.pop("center")
        zoom = kwargs.pop("zoom")
        camera = SimpleCamera(size, center, 3 / zoom)
        fractal = Fractal(camera, **kwargs)

    if dry:
        print(fractal)
        return

    image = fractal.render(True)
    save(image, output_file)


cli.add_command(bot)


if __name__ == "__main__":
    cli()
