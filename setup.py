#!/usr/bin/env python3

from setuptools import setup

try:
    with open("readme.md") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "{random, gui, cli} fractal generator"


setup(
    name="brocoli",
    version="0.0.1",
    packages=["brocoli"],
    url="https://github.com/ddorn/brocoli",
    license="MIT",
    author="Diego Dorn",
    author_email="diego.dorn@free.fr",
    description="{random, gui, cli} fractal generator",
    long_description=long_description,
    install_requires="tweepy numba numpy click pillow colour".split(),
    extras_require={"gui": ["kivy", "kivymd"]},
    entry_points={"console_scripts": ["brocoli = brocoli.brocoli:cli"]},
    include_package_data=True,
    keywords="fractal",
)
