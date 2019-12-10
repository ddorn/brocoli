#!/usr/bin/env python3

from math import log
from random import randint, randrange

import numpy as np
from numba import njit, prange
import click

from camera import SimpleCamera


__all__ = ['compute']

@njit(cache=True)
def f(z, c):
    return z * z + c


@njit(cache=True)
def escape(c, limit=50, f=f):
    z = 0j
    for i in range(1, limit):
        z = f(z, c)
        if abs(z) > 2:
            return i
    return -limit


@njit(cache=True)
def escape_smooth(c, limit=50, f=f):
    bound = 100
    z = 0j
    for i in range(1, limit):
        z = f(z, c)
        if abs(z) > bound:
            return i + log(log(bound) / log(abs(z))) / log(2)
    return -limit


@njit(cache=True)
def escape_angle(c, limit=50, f=f):
    z = 0j
    orbit = [z]

    for i in range(1, limit):
        z = f(z, c)
        orbit.append(z)

        if abs(z) > 2:
            break

    # transform orbit into value
    s = 0j
    for z in orbit:
        s += z
    return -abs(s) / len(orbit)


@njit(cache=True)
def escape_smoothfire(c, limit=50, f=f):
    ln12 = 1 / log(2)
    bound = 200_000_000
    lnbound = log(bound)

    absc = abs(c)
    z = c
    absz = abs(z)
    t = old_t = i = 0
    for i in range(1, limit):
        z = f(z, c)

        old_t = t
        absz = abs(z)
        zc = abs(z - c)
        m = abs(zc - absc)
        M = zc + absc

        if i > 1 and M != m:
            t += (absz - m) / (M - m)

        if absz > bound:
            if i < 3:
                return 0

            d = 1 + ln12 * log(lnbound / abs(log(absz)))
            # print(d)
            s1 = t / (i - 1)
            s0 = old_t / (i - 2)
            return d * s1 + (1 - d) * s0
            # return i + d

    d = 1 + ln12 * log(lnbound / abs(log(absz)))
    s1 = t / (i - 1)
    s0 = old_t / (i - 2)
    return -(d * s1 + (1 - d) * s0)


def random_position():
    size = (50, 50)
    limits = 200

    iterations = randint(3, 15)
    surf = np.empty(size)
    camera = SimpleCamera(size, -0.75, 3)

    for i in range(iterations):
        compute(camera, limits, 0, out=surf)

        # now we find a pixel on the border and zoom there
        done = False
        while not done:
            x, y = randrange(1, size[0] - 1), randrange(1, size[1] - 1)
            if surf[x, y] < 0:
                # we are inside, but are we on the border ?
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        # one of the neighbors is not in the set
                        if surf[x + dx, y + dy] > 0:
                            done = True
        camera.center = camera.complex_at((x, y))
        camera.height /= 3
    camera.height *= 3

    return camera


@njit(parallel=True, cache=True)
def _compute(out, bottomleft, pixstep, limits, kind=2):
    """
    Compute the escape time of each points of the surf.

    The camera is positioned with bottomleft and the zoom with pixstep.
    Limits is the maximum number of iterations.
    """

    w, h = out.shape
    for x in prange(w):
        a = bottomleft.real + pixstep * x
        for y in prange(h):
            b = bottomleft.imag + pixstep * (h - y - 1)

            c = a + b * 1j

            if kind == 1:
                r = escape_smooth(c, limits)
            elif kind == 2:
                r = escape_angle(c, limits)
            elif kind == 3:
                r = escape_smoothfire(c, limits)
            else:
                r = escape(c, limits)

            out[x, y] = r


def compute(camera: SimpleCamera, limits, kind, out=None):
    """
    Compute the view of the Mandelbrot set defined by the camera.

    The points inside the mandelbrot set always have a negative
    value, whose range depends on the kind of coloring function
    This is a convenience function for _compute.

    :param limits: maximum number of iterations
    :param kind:
        0: traditional escape time
        1: smooth escape time
        2: bugged smooth escape time
        3: triangle inequality average
    :param out: out array. If none is specified a new one is made.
    :return: a ndarray of dimension :camera.size: with the values of the
        coloring function on each complex point inside the frame.
        If :out: is not None, then the return array is out.
    """

    if out is None:
        out = np.empty(camera.size)
    else:
        assert tuple(camera.size) == out.shape, f"The camera and out array have different sizes. {camera.size} != {out.shape}"
    _compute(out, camera.bottomleft, camera.step, limits, kind)
    return out

@click.command()
@click.argument('centerx', default=-0.75)
@click.argument('centery', default=0.0)
@click.argument('zoom', default=2.0)
@click.option('--width', '-w', default=1920)
@click.option('--height', '-h', default=1080)
@click.option('--out', '-o', default='out.frac')
@click.option('--show', is_flag=True)
@click.option('--steps', '-s', default=100)
def main(width, height, centerx, centery, zoom, out, show):
    size = (width, height)
    camera = SimpleCamera(size, centerx + 1j * centery, zoom)

    print("Computing fractal")
    surf = compute(camera, 100, 3)

    print(f"Saving to {out}.npy")
    np.save(out, surf)

    if show:
        import seaborn as sns
        from matplotlib import pyplot as plt
        ax = sns.heatmap(surf.swapaxes(0, 1))
        plt.show()


if __name__ == '__main__':
    main()
