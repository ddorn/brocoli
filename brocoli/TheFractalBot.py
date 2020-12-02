#!/usr/bin/env python3

from io import BytesIO

import click

from .processing.random_fractal import random_fractal


def caption(fractal):

    real = fractal.camera.center.real
    imag = fractal.camera.center.imag
    height = fractal.camera.height
    text = f"""#DailyFractal #Fractal
#Mandelbrot set at {real}{imag :+}i
Zoom: {round(1/height)}
Steps: {fractal.limit}
Kind: {fractal.kind.value}
"""
    return text


def tweet_fractal(fractal, api, comment="", image=None):
    """
    Tweet a Fractal.

    :param Fractal fractal: A fractal object to render and tweet
    :param key_and_secrets: A 4-tuple of consumer key, secret and access key, secret
    """

    # Computing tweet

    if image is None:
        image = fractal.render(True)

    text = caption(fractal)
    if comment and len(text) + len(comment) < 279:
        text += "\n" + comment
        comment = None

    # Tweet

    filename = "random_fractal.jpg"
    image.save(filename, "jpeg")
    media = api.media_upload(filename)
    tweet = api.update_status(text, media_ids=[media.media_id])

    if comment:
        # it doesn't fit beneath the fractal description
        api.update_status(comment, in_reply_to_status_id=tweet.id)


@click.group(chain=True)
@click.pass_context
def bot(ctx):
    ctx.obj = {}
    fractal = random_fractal()
    ctx.obj["fractal"] = fractal
    ctx.obj["image"] = fractal.render(True)


@bot.command()
@click.argument("consumer-key", envvar="TWITTER_CONSUMER_KEY")
@click.argument("consumer-secret", envvar="TWITTER_CONSUMER_SECRET")
@click.argument("access-key", envvar="TWITTER_ACCESS_KEY")
@click.argument("access-secret", envvar="TWITTER_ACCESS_SECRET")
@click.option("--comment")
@click.pass_context
def twitter(ctx, consumer_key, consumer_secret, access_key, access_secret, comment):
    """
    Tweet a random fractal.

    All the twitter secrets can be in environment variables named
    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET
    """

    import tweepy

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    try:
        # ry to get a response from twitter
        api.rate_limit_status()
    except tweepy.TweepError as e:
        # if we can't, we stop here
        click.secho(
            "Impossible to connect with Twitter: "
            + e.response.json()["errors"][0]["message"],
            fg="red",
        )
        quit(1)

    fractal = ctx.obj["fractal"]
    image = ctx.obj["image"]
    tweet_fractal(fractal, api, comment, image)


@bot.command()
@click.argument("username", envvar="INSTAGRAM_USERNAME")
@click.argument("password", envvar="INSTAGRAM_PASSWORD")
@click.option("--comment")
@click.pass_context
def instagram(ctx, username, password, comment):
    fractal = ctx.obj["fractal"]
    image = ctx.obj["image"]

    raise NotImplementedError("Instagram as bad api.")

    from instapy_cli import client

    photo_path = "tmp_insta_fractal.jpg"
    image.save(photo_path)

    cap = caption(fractal)
    if comment:
        cap += "\n" + comment

    with client(username, password) as cli:
        cli.upload(photo_path, cap)

    print("Instagram post done!")
