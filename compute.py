#!/usr/bin/env python3
from enum import Enum
from math import log
from random import randint, randrange

import numpy as np
from numba import njit, prange
import click

from camera import SimpleCamera

__all__ = ['compute', 'random_position', 'Coloration', 'ESCAPE_FUNCTIONS']

DEFAULT_BOUND = 200_000


@njit
def f(z, c):
    # return z * z + -0.7487144+0.06478j
    # return z * z + 0.40925-0.21053j
    # return z * z + -0.10116598-0.8358299j
    return z * z + c


@njit
def escape(z0, c, limit=50, bound=DEFAULT_BOUND, f=f):
    z = z0
    for i in range(1, limit):
        z = f(z, c)
        if abs(z) > bound:
            return i
    return -limit


@njit
def escape_smooth(z0, c, limit=50, bound=DEFAULT_BOUND, f=f):
    z = z0
    for i in range(1, limit):
        z = f(z, c)
        if abs(z) > bound:
            return i + log(log(bound) / log(abs(z))) / log(2)
    return -limit


@njit
def escape_angle(z0, c, limit=50, bound=DEFAULT_BOUND, f=f):
    z = z0
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


@njit
def escape_smoothfire(z0, c, limit=50, bound=DEFAULT_BOUND, f=f):
    ln12 = 1 / log(2)
    lnbound = log(bound)

    absc = abs(c)
    z = z0
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


class Coloration(Enum):
    TIME = 'escape time'
    SMOOTH_TIME = 'smooth escape time'
    ANGLE = 'angle'
    AVG_TRIANGLE_INEQUALITY = 'average triangle inequality'


ESCAPE_FUNCTIONS = {
    Coloration.TIME: escape,
    Coloration.SMOOTH_TIME: escape_smooth,
    Coloration.ANGLE: escape_angle,
    Coloration.AVG_TRIANGLE_INEQUALITY: escape_smoothfire
}


@njit(parallel=True)
def _compute(out, escape_func, bottomleft, pixstep, limit, bound=100_000., julia=None):
    """
    Compute the escape time of each points of the surf.

    The camera is positioned with bottomleft and the zoom with pixstep.
    Limits is the maximum number of iterations.
    """

    w, h = out.shape
    for x in prange(w):
        for y in prange(h):
            z0 = bottomleft + pixstep * complex(x, h - y -1)

            if julia is None:
                out[x, y] = escape_func(z0, z0, limit, bound)
            else:
                out[x, y] = escape_func(z0, julia, limit, bound)


def compute(camera: SimpleCamera, kind: Coloration, out=None, limit=50, bound=DEFAULT_BOUND, julia=None):
    """
    Compute the view of the Mandelbrot set defined by the camera.

    The points inside the mandelbrot set always have a negative
    value, whose range depends on the kind of coloring function
    This is a convenience function for _compute.

    :param limits: maximum number of iterations
    :param kind: type of coloration function
    :param out: out array. If none is specified a new one is made.
    :return: a ndarray of dimension :camera.size: with the values of the
        coloring function on each complex point inside the frame.
        If :out: is not None, then the return array is out.
    """

    if out is None:
        # apparently we cannot create a numpy array of dynamic size inside a numba-compiled
        # function, so we create it here if needed
        out = np.empty(camera.size)
    else:
        assert tuple(
            camera.size) == out.shape, f"The camera and out array have different sizes. {camera.size} != {out.shape}"

    escape_func = ESCAPE_FUNCTIONS[kind]
    _compute(out, escape_func, camera.bottomleft, camera.step, limit, bound, julia)

    return out


def random_position():
    size = (50, 50)
    limits = 200

    iterations = randint(3, 15)
    surf = np.empty(size)
    camera = SimpleCamera(size, -0.75, 3)

    for i in range(iterations):
        compute(camera, Coloration.TIME, out=surf, limit=limits)

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
    surf = compute(camera, Coloration.AVG_TRIANGLE_INEQUALITY, limit=300)

    print(f"Saving to {out}.npy")
    np.save(out, surf)

    if show:
        import seaborn as sns
        from matplotlib import pyplot as plt
        ax = sns.heatmap(surf.swapaxes(0, 1))
        plt.show()


if __name__ == '__main__':
    main()
