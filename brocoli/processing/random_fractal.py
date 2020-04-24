#!/usr/bin/env python3

import logging
from pathlib import Path
import random

import numpy as np
import requests

from brocoli.processing.gradients import GradientGA
from .camera import SimpleCamera
from .colors import gradient
from .compute import Coloration, compute, timeit
from ..fractal import Fractal


logger = logging.getLogger("brocoli")


def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def random_kind():
    # return choice([Coloration.SMOOTH_TIME, Coloration.AVG_TRIANGLE_INEQUALITY])
    return random.choice(
        [e for e in Coloration if e not in (Coloration.TIME, Coloration.ANGLE)]
    )


def random_position():
    size = (50, 50)
    limits = 200

    iterations = random.randint(3, 15)
    surf = np.empty(size)
    camera = SimpleCamera(size, -0.75, 3)

    for i in range(iterations):
        compute(camera, Coloration.TIME, out=surf, limit=limits)

        # now we find a pixel on the border and zoom there
        done = False
        while not done:
            x, y = random.randrange(1, size[0] - 1), random.randrange(1, size[1] - 1)
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


def random_gradient_older():
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

    try:
        result = requests.post("http://colormind.io/api/", data=data, timeout=2)
        points = result.json()["result"]
        return points
        return list(gradient(*points, steps=1000, loop=True))
    except Exception as e:
        print(e)

        loop = True
        gradients = [
            "0F4152 59A07B F7E491 EDB825 EB3615",
            "D3AD2B D02C22 223336 326C67 187C25",
            "39624D 63A26E C6B070 E47735 A62413",
            "D83537 DD8151 F1DC81 7CCB86 4C5C77",
            "01ACD7 68C6C9 EFDC85 EB9821 9F290E",
            "000000 ff0000 000000 ffffff",
            "78ACDA 143986 0F1529 226197 8F82E2",
            "1F1D21 108D90 F5B33E FA7252 DA4D3F",
            "10182D 080908 D0490C DCAF14 F7EE51",
            "236261 14A087 93CC9D FDC97E ED3533",
            "FAFAFA F0CA32 F3431B 67221B 0B0C0D",
            "0E0E0E 40160E C7341B E78F2A F6F5F2",
            "244D5D 10A8D6 DCCDC1 C7794A CC4B3D",
            "073D52 10A8D6 F2E8DA F2903A B94C23",
            "05435F 099086 71D280 EFE84D F4B842",
        ]
        return random.choice(gradients).split()
        grad = random.choice(gradients).split()
        print(grad)
        return list(gradient(*grad, steps=1000, loop=True))


def random_gradient_old():
    """Get a random gradient from the gradients file."""
    path = Path(__file__).parent.parent / "data" / "gradients"
    gradients = path.read_text().splitlines()
    # First line is a comment, we replace it
    gradients[0] = gradients[-1]
    return random.choice(gradients).split()


def random_gradient():
    return random_gradient_old()
    ga = GradientGA(50)
    ga.evolve(20)
    return ga.best_RGB()


def optimal_limit(camera):
    camera = SimpleCamera((50, 50), camera.center, camera.height)

    # we use a dichotomy on n to find which 2**n
    # there is less than 50 pixels that changes in a 50x50 image
    n = 6
    last = 0
    while n < 13:
        n += 1
        new = compute(camera, Coloration.TIME, limit=2 ** n)

        escaped = (new > 0).sum()
        if escaped - last < 30 and escaped > 0:
            break

        last = escaped

    return 2 ** n


def random_fractal(size=(1920, 1080), seed=None):

    seed = str(seed)
    random.seed(seed)

    with timeit("Finding view point"):
        camera = random_position()

    with timeit("Random gradient"):
        gradient = random_gradient()

    with timeit("Optimal limit"):
        limit = optimal_limit(camera)
    logger.info("Limit: %s", limit)

    kind = random_kind()
    not_average = kind in (Coloration.SMOOTH_TIME, Coloration.TIME)
    speed = 1 + not_average
    camera.size = size
    bound = 2 ** random.randint(1, 20)

    fractal = Fractal(
        camera,
        kind=kind,
        limit=limit,
        bound=bound,
        normalize_quantiles=not_average,
        gradient_points=gradient,
        gradient_speed=speed,
        gradient_offset=0,
        inside_color=None,
        seed=seed,
    )

    return fractal


if __name__ == "__main__":
    from PIL import Image

    with timeit("Total"):
        print()
        fractal = random_fractal()
        with timeit("Rendering"):
            surf = fractal.render()

        image = Image.fromarray(surf, mode="RGB")

        name = "random_fractal.png"
        with timeit("Saving"):
            image.save(name)
        print(f"Saved as {name}")
        print("Done.")

    image.show()
