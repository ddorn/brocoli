import numpy as np
from kivy.properties import NumericProperty, BooleanProperty, ReferenceListProperty, ObjectProperty

from colorize import normalize_quantiles
from tabs.base import MyTab


class PreprocTab(MyTab):
    steps_power = NumericProperty(1)
    normalize_quantiles = BooleanProperty()
    speed = NumericProperty(1)
    offset = NumericProperty(0)

    any = ReferenceListProperty(speed,
                                offset,
                                steps_power,
                                normalize_quantiles)

    fractal = ObjectProperty(force_dispatch=True, allownone=True)
    preproc_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(any=self.process, fractal=self.process)

    def process(self, *args, **kwargs):

        print('PreprocTab.process', kwargs)

        # if no keyword, cache the fractal it is the one for the view
        cache = kwargs.pop('cache', len(kwargs) == 0)
        fractal = kwargs.pop('fractal', self.fractal)
        norm_quantiles = kwargs.pop('normalize_quantiles', self.normalize_quantiles)
        steps_power = kwargs.pop('steps_power', self.steps_power)
        speed = kwargs.pop('speed', self.speed)
        offset = kwargs.pop('offset', self.offset)

        if kwargs:
            print(f"Warning: GradientTab.process had unknown kwargs {tuple(kwargs.keys())}.")

        if fractal is None:
            print('Warning: GradientTab.process called without fractal.')
            return

        fractal = fractal.copy()

        # we don't want a constant image
        if speed == 0:
            speed = 1

        if norm_quantiles:
            fractal = normalize_quantiles(fractal, 1000)

        if steps_power not in (0, 1):
            # signed power
            fractal = abs(fractal) ** steps_power * np.sign(fractal)

        # put fractal between 0 and 1
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

        print(np.nanmin(fractal), np.nanmax(fractal))

        if cache:
            self.preproc_fractal = fractal
        else:
            return fractal