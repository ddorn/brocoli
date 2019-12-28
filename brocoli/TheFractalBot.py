#!/usr/bin/env python3

import os
from io import BytesIO

import tweepy

from .processing.random_fractal import random_fractal


def tweet_text(fractal):

    real = fractal.camera.center.real
    imag = fractal.camera.center.imag
    heigth = fractal.camera.height
    text = f"""#DailyFractal #Fractal
#Mandelbrot set at {real}{imag :+}i
Zoom: {round(1/heigth)}
Steps: {fractal.limit}
Kind: {fractal.kind.value}
"""
    return text


def tweet_random_fractal(api, comment):

    fractal = random_fractal()
    image = fractal.render(True)

    text = tweet_text(fractal)
    if comment and len(text) + len(comment) < 279:
        text += "\n" + comment
        comment = None

    bytes = BytesIO()
    image.save(bytes, "jpeg")
    tweet = api.update_with_media("random_fractal.jpg", text, file=bytes)

    if comment:
        # it doesn't fit beneath the fractal description
        api.update_status(comment, in_reply_to_status_id=tweet.id)


if __name__ == "__main__":
    CONSUMER_KEY = os.environ["TWITTER_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["TWITTER_CONSUMER_SECRET"]
    ACCESS_KEY = os.environ["TWITTER_ACCESS_KEY"]
    ACCESS_SECRET = os.environ["TWITTER_ACCESS_SECRET"]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    tweet_random_fractal(api)
