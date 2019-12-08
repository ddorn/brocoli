from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, ReferenceListProperty

from colorize import apply_gradient, normalize_quantiles
from colors import gradient, BLACK
from tabs.base import MyTab

import numpy as np


class GradientTab(MyTab):
    loop = BooleanProperty(True)
    speed = NumericProperty(1)
    offset = NumericProperty(0)
    black_inside = BooleanProperty(True)
    steps_power = NumericProperty(1)
    normalize_quantiles = BooleanProperty()

    any = ReferenceListProperty(loop,
                                speed,
                                offset,
                                black_inside,
                                steps_power,
                                normalize_quantiles)

    fractal = ObjectProperty(force_dispatch=True, allownone=True)
    colored_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.do_binds)

    def do_binds(self, *args):
        self.bind(any=self.process, fractal=self.process)

    def process(self, *args, **kwargs):

        print('GradientTab.process', kwargs)

        # if no keyword, cache the fractal it is the one for the view
        cache = kwargs.pop('cache', len(kwargs) == 0)

        fractal = kwargs.pop('fractal', self.fractal)
        loop  = kwargs.pop('loop', self.loop)
        speed = kwargs.pop('speed', self.speed)
        offset = kwargs.pop('offset', self.offset)
        black_inside = kwargs.pop('black_inside', self.black_inside)

        if kwargs:
            print(f"Warning: GradientTab.process had unknown kwargs {tuple(kwargs.keys())}.")

        if fractal is None:
            print('Warning: GradientTab.process called without fractal.')
            return

        # grad = list(grad('#0F4152', '#59A07B', '#F7E491', '#EDB825', '#EB3615', loop=loop))
        # grad = list(grad('#7d451b', '#78bc61', '#e3d26f', '#e3d26f', loop=loop))
        # grad = list(grad(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=loop))
        # grad = [hsv_to_RGB(h / 1000, 1 , 1) for h in range(1000)]
        # grad = list(grad(*"39624D 63A26E C6B070 E47735 A62413".split(), loop=loop))
        grad = list(gradient(*"FFD500 FFA500 864A29 000080 F2F2E9".split(), loop=loop))
        # grad = list(grad(*"D83537 DD8151 F1DC81 7CCB86 4C5C77".split(), loop=loop))
        # grad = list(grad(*"01ACD7 68C6C9 EFDC85 EB9821 9F290E".split(), loop=loop))

        # if black_inside:
        #     grad.append(BLACK)

        if self.normalize_quantiles:
            fractal = normalize_quantiles(fractal, len(grad))


        image = apply_gradient(fractal, grad, speed, offset)

        if self.black_inside:
            image[self.fractal >= self.brocoli.camera_tab.steps] = (0, 0, 0)

        if cache:
            if self.colored_fractal is not None:

                print(image.shape, self.colored_fractal.shape)
                eq = self.colored_fractal == image
                if (isinstance(eq, bool) and not eq) or eq.all():
                    print('damn it')
            self.colored_fractal = image
        else:
            return image