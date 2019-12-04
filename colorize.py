#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt

from colors import gradient


def apply_gradient(surf: np.ndarray, gradient, speed=1.0, offset=0.0):
    gradient = np.array(gradient, dtype=np.int8)

    mini = np.nanmin(surf)
    maxi = np.nanmax(surf)

    normalised = ((surf - mini) / (maxi - mini) * speed + offset) % 1.0
    normalised *= (len(gradient) - 1)
    normalised[~np.isfinite(normalised)] = 0

    out = gradient[normalised.astype(np.int)]

    return out

def normalize_quantiles(surf, nb, exclude_max=True):
    """
    Discretize the array such that every number has approximately the same area.

    Preserves the order (ie surf[x] <= surf[y] => f(surf)[x] < f(surf)[y])

    :param surf: ndarray to process
    :param nb: nb of discrete values in the return
    :return: ndarray with the same shape and discrete values.
    """

    values = np.sort(surf.flatten())
    end = values.size if not exclude_max else values.searchsorted(values[-1])
    indices = (np.linspace(0, 1, nb, endpoint=False) * end).astype(int)
    steps = values[indices]

    new = np.empty(surf.shape)
    for part, bound in enumerate(steps):
        new[surf >= bound] = part

    return new.reshape(surf.shape)

if __name__ == '__main__':
    surf = np.load('out.frac.npy')
    grad = tuple(gradient((0, 0, 0), (255, 169, 0), steps=255))

    out = apply_gradient(surf, grad)

    from PIL import Image
    im = Image.fromarray(out.swapaxes(0,1), 'RGB')
    im.show(command='feh')
    quit()

    import seaborn as sns
    ax = sns.heatmap(out.swapaxes(0,1))
    plt.show()


