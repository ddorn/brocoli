#!/usr/bin/env python3
from cmath import phase
from collections import deque
from contextlib import contextmanager
from enum import Enum
from math import log
from time import time

import numpy as np
from numba import njit, prange
import click

from .camera import SimpleCamera

__all__ = ["compute", "Coloration", "ESCAPE_FUNCTIONS"]

DEFAULT_BOUND = 200_000


@njit
def lerp(a, b, t):
    """
    Linear interpolation between `a` and `b`.

    Return `a` when `t` is 0 and `b` when `t` is one.
    """

    return a * (1.0 - t) + b * t


@njit
def smooth_coef(z, bound):
    z = abs(z)
    d = 1 + 1 / log(2) * log(log(bound) / abs(log(z))) if z != 1 else 0
    return d


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
    s = s1 = i = 0
    sign = 1
    for i in range(1, limit):
        z = f(z, c)

        s1 = s
        absz = abs(z)
        zc = abs(z - c)
        m = abs(zc - absc)
        M = zc + absc

        if i > 1 and M != m:
            s += (absz - m) / (M - m)

        if absz > bound:
            break
    else:
        sign = -1

    d = 1 + ln12 * log(lnbound / abs(log(absz))) if absz != 1 else 0
    S = s / (i - 1) if i > 1 else 0
    S1 = s1 / (i - 2) if i > 2 else 0
    return lerp(S1, S, d) * sign


# @njit
# def escape_curvature(z0, c, limit=50, bound=DEFAULT_BOUND, f=f):
#     z1 = 0
#     z = z0
#
#     s = s1 = 0
#     sign = 1
#     i = 0
#     for i in range(limit):
#         z, z1, z2 = f(z, c), z, z1
#
#         if i >= 2 and (z1 != z2):
#             angle = (z - z1) / (z1 - z2)
#             s, s1 = s + abs(phase(angle)), s
#
#         if abs(z) > bound:
#             break
#     else:
#         sign = -1
#
#     # noinspection PyUnboundLocalVariable
#     S = s / (i - 1) if i > 1 else 0
#     S1 = s1 / (i - 2) if i > 2 else 0
#     d = 1 + 1 / log(2) * log(log(bound) / abs(log(abs(z)))) if abs(z) != 1 else 0
#     if sign < 0:
#         return -1
#     return lerp(S1, S, d) * sign


@njit
def my_deque_push(deque, head, value):
    deque[head] = value
    head = (head + 1) % len(deque)
    return head


def addend(order):
    def decorator(t):
        t = njit(t)

        @njit
        def func(z0, c, limit=50, bound=DEFAULT_BOUND, f=f):
            # last `order` iterates of the function
            # Ideally we would like to use a deque but numba does
            # not support them, so we will use a list and a end/start
            # pointer. Which works fine, since the deque has constant size
            # after order iterations
            zs = [0j] * order
            head = 0  # this is always a valid index one after the last pushed value
            head = my_deque_push(zs, head, z0)
            # partial sums
            s = s1 = i = 0

            sign = 1
            for i in range(limit):
                head = my_deque_push(zs, head, f(zs[head - 1], c))

                if i >= order - 1:
                    s1, s = s, s + t(zs, head)

                if abs(zs[head - 1]) > bound:
                    break
            else:
                # we are inside, so negative values
                sign = -1

            S = s / (i - order + 2) if i > order - 2 else 0
            S1 = s1 / (i - order + 1) if i > order - 1 else 0
            d = smooth_coef(zs[head - 1], bound)
            return lerp(S1, S, d) * sign

        return func

    return decorator


@addend(3)
def escape_curvature(zs, head):
    if zs[head - 2] == zs[head]:
        return 0
    angle = (zs[head - 1] - zs[head - 2]) / (zs[head - 2] - zs[head])
    return abs(phase(angle))


class Coloration(Enum):
    TIME = "escape time"
    SMOOTH_TIME = "smooth escape time"
    ANGLE = "angle"
    AVG_TRIANGLE_INEQUALITY = "average triangle inequality"
    AVG_CURVATURE = "average curvature"


ESCAPE_FUNCTIONS = {
    Coloration.TIME: escape,
    Coloration.SMOOTH_TIME: escape_smooth,
    Coloration.ANGLE: escape_angle,
    Coloration.AVG_TRIANGLE_INEQUALITY: escape_smoothfire,
    Coloration.AVG_CURVATURE: escape_curvature,
}


@njit(parallel=True)
def _compute(out, escape_func, bottomleft, pixstep, limit, bound=100_000.0, julia=None):
    """
    Compute the escape time of each points of the surf.

    The camera is positioned with bottomleft and the zoom with pixstep.
    Limits is the maximum number of iterations.
    """

    w, h = out.shape
    for x in prange(w):
        for y in range(h):
            z0 = bottomleft + pixstep * complex(x, h - y - 1)

            if julia is None:
                out[x, y] = escape_func(z0, z0, limit, bound)
            else:
                out[x, y] = escape_func(z0, julia, limit, bound)


def compute(
    camera: SimpleCamera,
    kind: Coloration,
    out=None,
    limit=50,
    bound=DEFAULT_BOUND,
    julia=None,
):
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
        assert (
            tuple(camera.size) == out.shape
        ), f"The camera and out array have different sizes. {camera.size} != {out.shape}"

    escape_func = ESCAPE_FUNCTIONS[kind]
    _compute(out, escape_func, camera.bottomleft, camera.step, limit, bound, julia)

    return out


@contextmanager
def timeit(text=""):
    t = time()
    if text:
        print(f"{text}..." + " " * (21 - len(text)), end="", flush=True)
    yield
    print(f"{round(time() - t, 2)}s")


@click.command()
@click.argument("centerx", default=-0.75)
@click.argument("centery", default=0.0)
@click.argument("zoom", default=2.0)
@click.option("--width", "-w", default=1920)
@click.option("--height", "-h", default=1080)
@click.option("--out", "-o", default="out.frac")
@click.option("--show", is_flag=True)
@click.option("--steps", "-s", default=100)
def main(width, height, centerx, centery, steps, zoom, out, show):
    size = (width, height)
    camera = SimpleCamera(size, centerx + 1j * centery, zoom)

    print("Computing fractal")
    surf = compute(camera, Coloration.AVG_CURVATURE, limit=300)

    # print(f"Saving to {out}.npy")
    # np.save(out, surf)

    if show:
        import seaborn as sns
        from matplotlib import pyplot as plt

        ax = sns.heatmap(surf.swapaxes(0, 1))
        plt.show()


if __name__ == "__main__":
    main()
