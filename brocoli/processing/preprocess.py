import numpy as np


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
    zero = steps.searchsorted(0, "right") if exclude_inside else 0

    new = np.empty(surf.shape)
    for part, bound in enumerate(steps):
        new[surf >= bound] = part - zero

    return new.reshape(surf.shape)


def do_bins(surf, nb):
    """
    Modify the array such that [nb] parts have the same size and the same range.

    Preserves the order (ie surf[x] < surf[y] => f(surf)[x] < f(surf)[y]).
    Example:
        bins(surf, 2) maps half of the surface to [0, 1] and the other half to [1, 2].
    """

    assert nb >= 1

    inside = (surf < 0)

    values = np.sort(surf[~inside].flatten())

    if values.size < nb + 1:
        return surf  # less values than bins

    indices = (np.linspace(0, 1, nb+1, endpoint=True) * values.size).astype(int)
    indices[-1] -= 1  # We want the last value in the array
    boundaries = values[indices]
    zero = boundaries.searchsorted(0, "right")
    print(zero)

    new = surf.copy()
    last = boundaries[0]
    for part, bound in enumerate(boundaries[1:]):
        mask = (last <= surf) & (surf <= bound)
        new[mask] = part - zero + (surf[mask] - last) / (bound - last)
        last = bound

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

    return fractal


def signed_power(fractal, power):
    """
    Raise every point to the given power, keeping the sign.

    :return: abs(fractal) ** power * sign(fractal)
    """
    return abs(fractal) ** power * np.sign(fractal)


def preprocess(fractal, bins=1, norm_quantiles=False, steps_power=1):
    """
    Normalise the values of the fractal before coloration.

    Each argument corresponds to a additional transformation.
    This is a function from R^(mn) to [-1, -1]^(mn). This keeps
    the sign of the inputs.

    :param bins_: apply bins with the corresponding number (>=1)
    :param norm_quantiles: whether to apply normalize_quantiles()
    :param steps_power: raise the fractal to a given power, to emphasis
        on low or high escape times
    :return:
    """

    if bins > 1:
        fractal = do_bins(fractal, bins)

    if norm_quantiles:
        fractal = normalize_quantiles(fractal, 1000)

    if steps_power not in (0, 1):
        fractal = signed_power(fractal, steps_power)

    return signed_normalize_ip(fractal)


if __name__ == "__main__":
    a = np.array(range(12), dtype=float).reshape((3, 4))
    a[1] = [1, 1.1, 1.2, 1.4]

    print(a)

    print(do_bins(a, 2))


