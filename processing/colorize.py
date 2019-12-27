#!/usr/bin/env python3

import numpy as np

from processing.colors import gradient


def apply_gradient(surf: np.ndarray, gradient, speed=1.0, offset=0.0):
    """
    Apply a gradient to a surface with values in [0,1].

    A value of 0 is the beginning o the gradient and 1 is this end.
    This function is from [0,1]^(m,n) -> [0,255]^(m,n,3)

    :param surf: array wih values between 0 and 1
    :param gradient: list of colors
    :param speed: speed of the gradient. A speed of 2 would make the gradient
        loop twice. Once between 0 and 0.5 aand once between 0.5 and 1
    :param offset: The gradient offset tells what value in surf corresponds
        to gradient[0]
    :return: An image of shape (m, n, 3) of int8.
    """
    gradient = np.array(gradient, dtype=np.int8)

    mini = np.nanmin(surf)
    maxi = np.nanmax(surf)

    normalised = ((surf - mini) / (maxi - mini) * speed + offset) % 1.0
    normalised *= len(gradient) - 1
    normalised[~np.isfinite(normalised)] = 0

    out = gradient[normalised.astype(np.int)]

    return out


def colorize(
    fractal,
    gradient_points,
    speed=1,
    offset=0,
    loop=False,
    inside_color=None,
    color_count=1000,
):
    loop = loop or (speed != 1) or (offset != 0)

    if color_count is not None:
        grad = list(gradient(*gradient_points, steps=color_count, loop=loop))
    else:
        grad = gradient_points

    image = apply_gradient(abs(fractal), grad, speed, offset)

    if inside_color is not None:
        image[fractal < 0] = inside_color

    return image


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    surf = np.load("out.frac.npy")
    grad = tuple(gradient((0, 0, 0), (255, 169, 0), steps=255))

    out = apply_gradient(surf, grad)

    from PIL import Image

    im = Image.fromarray(out.swapaxes(0, 1), "RGB")
    im.show(command="feh")
    quit()

    import seaborn as sns

    ax = sns.heatmap(out.swapaxes(0, 1))
    plt.show()
