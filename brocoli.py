#!/usr/bin/env python3

import click

from fractal import Fractal
from processing import SimpleCamera, Coloration
from processing.compute import timeit


@click.group()
def cli():
    pass


@cli.command()
def gui():
    from kivymain import BrocoliApp

    BrocoliApp().run()


@cli.command()
@click.argument("width", default=1920)
@click.argument("height", default=1080)
@click.option("--show", "-s", is_flag=True)
@click.option("--out", "-o", default="random_fractal.png")
def random(width, height, show, out):
    from processing.random_fractal import random_fractal
    from PIL import Image

    fractal = random_fractal((width, height))
    with timeit("Rendering"):
        surf = fractal.render()

    image = Image.fromarray(surf, mode="RGB")
    image.save(out)
    print(f"Image saved as {out}")

    if show:
        image.show()


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
