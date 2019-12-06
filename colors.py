def mix(a, b, f):
    return [round(aa * (1-f) + bb * f ) for aa, bb in zip(a, b)]


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

    nb_segments = len(colors) - 1
    a = colors[0]
    b = colors[1]
    segment = 1
    for i in range(steps):
        pos = i / (steps - 1)
        if pos > segment / nb_segments:
            segment += 1
            a, b = b, colors[segment]
        seg_pos = pos * nb_segments - (segment - 1)
        c = mix(a, b, seg_pos)
        yield c

def hex2rgb(color: str):
    color = color.strip()
    color = color.strip('#')
    assert len(color) == 6

    return tuple(map(lambda i: int(color[i: i+2], 16), range(0, 6, 2)))
