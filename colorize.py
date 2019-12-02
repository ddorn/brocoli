#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt

from colors import gradient


def apply_gradient(surf: np.ndarray, gradient, speed, offset):
    gradient = np.array(gradient, dtype=np.int8)

    mini = np.nanmin(surf)
    maxi = np.nanmax(surf)

    normalised = ((surf - mini) / (maxi - mini) * speed + offset) % 1.0
    normalised *= (len(gradient) - 1)
    normalised[~np.isfinite(normalised)] = 0

    out = gradient[normalised.astype(np.int)]

    return out

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


