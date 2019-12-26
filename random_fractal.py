#!/usr/bin/env python3
from contextlib import contextmanager
from random import choice, randint, randrange, random
from time import time

import numpy as np
import requests

from camera import SimpleCamera
from colorize import signed_normalize_ip, apply_gradient, normalize_quantiles
from colors import gradient
from compute import Coloration, compute


def random_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def random_kind():
    return choice([Coloration.SMOOTH_TIME, Coloration.AVG_TRIANGLE_INEQUALITY])
    return choice([e for e in Coloration if e != Coloration.ANGLE])


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


def random_gradient():
    # grad = list(gradient('#0F4152', '#59A07B', '#F7E491', '#EDB825', '#EB3615', loop=True))
    # return grad

    # light = ['ffffff']
    # flash = []
    # dark = ['1a202c']
    # sexy_colors = 'ffa500 feb2b2 c53030 68d391 4fd1c5 3182ce 805ad5 d53f8c #fff200'.split()
    #
    # for c in sexy_colors:
    #     c = hex2rgb(c)
    #     h, s, v = rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    #
    #     light.append(hsv_to_RGB(h, s, 0.9))
    #     flash.append(hsv_to_RGB(h, s, v))
    #     dark.append(hsv_to_RGB(h, s, 0.1))
    #
    # shuffle(light)
    # shuffle(flash)
    # shuffle(dark)
    #
    # colors = [light[0], *flash[:2], dark[0]]
    # shuffle(colors)
    #
    # print(colors)
    #
    # return list(gradient(*colors, steps=1000, loop=True))
    #
    # return

    data = '{"model":"default"}'

    result = requests.post('http://colormind.io/api/', data=data)
    points = result.json()['result']
    return list(gradient(*points, steps=1000, loop=True))


def optimal_limit(camera):
    camera = SimpleCamera((50, 50), camera.center, camera.height)

    # we use a dichotomy on n to find which 2**n
    # there is less than 50 pixels that changes in a 50x50 image
    n = 6
    last = 0
    while n < 13:
        n += 1
        new = compute(camera, Coloration.TIME, limit=2**n)

        escaped = (new > 0).sum()
        if escaped - last < 30 and escaped > 0:
            break

        last = escaped

    return 2**n


@contextmanager
def timeit(text=''):
    t = time()
    if text:
        print(f'{text}...' + ' '*(21 - len(text)), end='')
    yield
    print(f'{round(time() - t, 2)}s')


def random_fractal(size=(1920, 1080)):


    with timeit('Finding view point'):
        camera = random_position()

    with timeit('Random gradient'):
        gradient = random_gradient()

    with timeit('Optimal limit'):
        limit = optimal_limit(camera)
    print('Limit:', limit)

    kind = random_kind()
    speed = 1 + (kind == Coloration.SMOOTH_TIME)
    camera.size = size

    with timeit('Computing'):
        frac = compute(camera, kind, limit=limit)

    with timeit('Pre-processing'):
        if kind != Coloration.AVG_TRIANGLE_INEQUALITY:
            frac = normalize_quantiles(frac, 1000)

        signed_normalize_ip(frac, speed)

    with timeit('Coloring'):
        if random() < 0.5:
            frac = apply_gradient(abs(frac), gradient)
        else:
            inside = random_color()
            frac = apply_gradient(frac, gradient, inside=inside)

    return frac


if __name__ == '__main__':
    from PIL import Image
    with timeit('Total'):
        print()
        frac = random_fractal()

        image = Image.fromarray(frac.swapaxes(0, 1), mode='RGB')

        name = 'random_fractal.png'
        with timeit('Saving'):
            image.save(name)
        print(f'Saved as {name}')
        print('Done.')

    image.show()
