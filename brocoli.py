#!/usr/bin/env python3

import click

from fractal import Fractal
from processing import SimpleCamera, Coloration
from processing.colors import hex2rgb
from processing.compute import timeit


def save(pil_image, click_file):
    """Save the image to the file and prints where it is saved. Handles stdout."""

    if "." in click_file.name:
        pil_image.save(click_file)
        print(f"Saved as {click_file.name}")
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


@click_type("coloration kind", hint="Coloration must be one of [S|A|T|I]")
def enum_type(val):
    d = {
        "a": Coloration.ANGLE,
        "t": Coloration.TIME,
        "s": Coloration.SMOOTH_TIME,
        "i": Coloration.AVG_TRIANGLE_INEQUALITY,
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


# ---- Definition of the command line interface ---- #


@click.group()
def cli():
    pass


@cli.command()
def gui():
    from kivymain import BrocoliApp

    BrocoliApp().run()


@cli.command()
@click.argument("size", type=size_type, default="1920x1080")
@click.option("--show", "-s", is_flag=True)
@output_file_option
def random(size, show, output_file):
    """Generate a random fractal of a given SIZE."""

    from processing.random_fractal import random_fractal
    from PIL import Image

    fractal = random_fractal(size)
    with timeit("Rendering"):
        surf = fractal.render()

    image = Image.fromarray(surf, mode="RGB")

    # if stdout is passed as output_file
    ext = None if "." in output_file.name else "jpeg"
    image.save(output_file, ext)

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
@click.option("--norm-quantiles", "-q", is_flag=True, help="Colors has the same area.")
@click.option("--steps-power", "-p", default=1.0, help="Enhance low or high values.")
@click.option(
    "--gradient",
    "-g",
    type=gradient_type,
    default=("0F4152-59A07B-F7E491-EDB825-EB3615"),
    help="Dash separeted hex colors. A trailing dash loops the gradient.",
)
@click.option("--color-count", "-c", default=256, help="Steps in the gradient.")
@click.option("--speed", "-s", default=1.0, help="Gradient speed.")
@click.option("--offset", "-S", default=0.0, help="Gradient offset.")
@click.option("--inside-color", "-i", type=color_type, help="Gradient offset.")
@click.option("--dry", "-d", is_flag=True, help="Print the fractal. Don't compute.")
@output_file_option
def gen(
    center,
    size,
    zoom,
    kind,
    limit,
    bound,
    julia,
    norm_quantiles,
    steps_power,
    gradient,
    color_count,
    speed,
    offset,
    inside_color,
    dry,
    output_file,
):

    camera = SimpleCamera(size, center, 3 / zoom)
    fractal = Fractal(
        camera=camera,
        kind=kind,
        limit=limit,
        bound=bound,
        julia=julia,
        normalize_quantiles=norm_quantiles,
        steps_power=steps_power,
        gradient_points=gradient,
        color_count=color_count,
        gradient_loop=False,  # can set with gradient_points
        gradient_speed=speed,
        gradient_offset=offset,
        inside_color=inside_color,
    )

    if dry:
        print(fractal)
        return

    image = fractal.render(True)
    save(image, output_file)


@cli.command()
@click.option("--consumer-key", envvar="TWITTER_CONSUMER_KEY")
@click.option("--consumer-secret", envvar="TWITTER_CONSUMER_SECRET")
@click.option("--access-key", envvar="TWITTER_ACCESS_KEY")
@click.option("--access-secret", envvar="TWITTER_ACCESS_SECRET")
def bot(consumer_key, consumer_secret, access_key, access_secret):
    import tweepy
    from TheFractalBot import tweet_random_fractal

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    tweet_random_fractal(api)


if __name__ == "__main__":
    cli()
