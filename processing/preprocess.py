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

    values =  np.sort(surf.flatten())
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

    return fractal


def signed_power(fractal, power):
    """
    Raise every point to the given power, keeping the sign.

    :return: abs(fractal) ** power * sign(fractal)
    """
    return abs(fractal) ** power * np.sign(fractal)


def preprocess(fractal, norm_quantiles=False, steps_power=1):
    """
    Normalise the values of the fractal before coloration.

    Each argument corresponds to a additional transformation.
    This is a function from R^(mn) to [-1, -1]^(mn). This keeps
    the sign of the inputs.

    :param norm_quantiles: whether to apply normalize_quantiles()
    :param steps_power: raise the fractal to a given power, to emphasis
        on low or high escape times
    :return:
    """

    if norm_quantiles:
        fractal = normalize_quantiles(fractal, 1000)

    if steps_power not in (0, 1):
        fractal = signed_power(fractal, steps_power)

    return signed_normalize_ip(fractal)
