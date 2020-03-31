from colorsys import rgb_to_hsv, hsv_to_rgb
import colour

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def mix(a, b, f):
    return [round(aa * (1 - f) + bb * f) for aa, bb in zip(a, b)]


def hsv_mix(a, b, f):
    if abs(a[0] - b[0]) < 0.5:
        h = a[0] * (1 - f) + b[0] * f
    elif a[0] > b[0]:
        h = (a[0] * (1 - f) + (b[0] + 1) * f) % 1
    else:
        h = (a[0] * (1 - f) + (b[0] - 1) * f) % 1

    s = a[1] * (1 - f) + b[1] * f
    v = a[2] * (1 - f) + b[2] * f
    return h, s, v


def hsv_to_RGB(h, s, v):
    r, g, b = hsv_to_rgb(h, s, v)
    return int(255 * r), int(255 * g), int(255 * b)


def RGB_to_hsv(r, g, b):
    return rgb_to_hsv(r / 255, g / 255, b / 255)


def to_hex(col):
    if isinstance(col, str):
        return "#" + col.strip("#")

    return "#" + "".join(hex(x)[2:] for x in col)


def gradient(*colors, steps=256, loop=False):
    """
    Yield the values of a colorisation as RGB tuple.
    :param colors: RGB tuples or hex strings
    :param steps: number of colors to generate
    """
    assert len(colors) >= 2, "There should be at least two colors in a gradient"
    colors = [hex2rgb(c) if isinstance(c, str) else c for c in colors]
    if loop:
        colors.append(colors[0])

    colors = [RGB_to_hsv(*c) for c in colors]

    nb_segments = len(colors) - 1
    a = colors[0]
    b = colors[1]
    segment = 1
    for i in range(steps):
        pos = i / (steps - 1)
        if pos > segment / nb_segments:
            segment += 1
            a, b = b, colors[segment]
        seg_pos = f = pos * nb_segments - (segment - 1)

        if abs(a[0] - b[0]) < 1 / 3 and abs(a[2] - b[2]) < 1.0 / 2:
            c = hsv_to_RGB(*hsv_mix(a, b, f))
        else:
            c = mix(hsv_to_RGB(*a), hsv_to_RGB(*b), seg_pos)
        yield c


def hex2rgb(color: str):
    color = color.strip()
    color = color.strip("#")

    if color.lower() in colour.COLOR_NAME_TO_RGB:
        return colour.COLOR_NAME_TO_RGB[color.lower()]
    assert len(color) == 6

    return tuple(map(lambda i: int(color[i : i + 2], 16), range(0, 6, 2)))
