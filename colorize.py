#!/usr/bin/env python3

import numpy as np

from colors import gradient


def apply_gradient(surf: np.ndarray, gradient, speed=1.0, offset=0.0, inside=None):
    gradient = np.array(gradient, dtype=np.int8)

    if inside is not None:
        mini = np.nanmin(surf[surf >= 0])
        maxi = np.nanmax(surf[surf >= 0])
    else:
        mini = np.nanmin(surf)
        maxi = np.nanmax(surf)

    normalised = ((surf - mini) / (maxi - mini) * speed + offset) % 1.0
    normalised *= (len(gradient) - 1)
    normalised[~np.isfinite(normalised)] = 0

    if inside is not None:
        normalised[surf < 0] = -1

    out = gradient[normalised.astype(np.int)]

    if inside is not None:
        out[surf < 0] = inside

    return out


def normalize_quantiles(surf, nb, exclude_inside=True):
    """
    Discretize the array such that every number has approximately the same area.

    Preserves the order (ie surf[x] <= surf[y] => f(surf)[x] < f(surf)[y])

    :param surf: ndarray to process
    :param nb: nb of discrete values in the return
    :param exclude_inside: keep the negative values negative
    :return: ndarray with the same shape and discrete values.
    """

    values = np.sort(surf.flatten())
    indices = (np.linspace(0, 1, nb, endpoint=False) * values.size).astype(int)
    steps = values[indices]
    zero = steps.searchsorted(0, 'right') if exclude_inside else 0

    new = np.empty(surf.shape)
    for part, bound in enumerate(steps):
        new[surf >= bound] = part - zero

    return new.reshape(surf.shape)


def signed_normalize_ip(fractal, speed=1.0, offset=0.0):
    """
    Normalize a fractal and keep the the sign of each value.

    Negative numbers are mapped to [-1, 0] and positive to [0, 1]
    The speed and offset rotate the normalized values.

    :param speed: rotation stretch
    :param offset: rotation
    :return: a ndarray with valuesbetween -1 and 1
    """

    pos = fractal[fractal >= 0]
    neg = fractal[fractal < 0]

    if pos.size > 0:
        mini = np.nanmin(pos)
        maxi = np.nanmax(pos)
        if mini != maxi:
            pos[:] = (pos - mini) / (maxi - mini)
            pos[:] = (pos * speed + offset) % 1.0
        else:
            pos[:] = 1

    if neg.size > 0:
        mini = np.nanmin(neg)
        maxi = np.nanmax(neg)
        if mini != maxi:
            neg[:] = (neg - maxi) / (maxi - mini)
            neg[:] = (neg * speed + offset) % 1.0 - 1
        else:
            neg[:] = -1

        assert (neg <= 0).all()

    fractal[fractal >= 0] = pos
    fractal[fractal < 0] = neg


def signed_power(fractal, power):
    """
    Raise every point to the given power, keeping the sign.

    :return: abs(fractal) ** power * sign(fractal)
    """
    return abs(fractal) ** power * np.sign(fractal)


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    surf = np.load('out.frac.npy')
    grad = tuple(gradient((0, 0, 0), (255, 169, 0), steps=255))

    out = apply_gradient(surf, grad)

    from PIL import Image

    im = Image.fromarray(out.swapaxes(0, 1), 'RGB')
    im.show(command='feh')
    quit()

    import seaborn as sns

    ax = sns.heatmap(out.swapaxes(0, 1))
    plt.show()
