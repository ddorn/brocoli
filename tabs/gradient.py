from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, ReferenceListProperty

from colorize import apply_gradient
from colors import gradient, BLACK
from tabs.base import MyTab


class GradientTab(MyTab):
    loop = BooleanProperty(True)
    black_inside = BooleanProperty(True)

    any = ReferenceListProperty(loop,
                                black_inside)

    preproc_fractal = ObjectProperty(force_dispatch=True, allownone=True)
    colored_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.do_binds)

    def do_binds(self, *args):
        self.bind(any=self.process, preproc_fractal=self.process)

    def process(self, *args, **kwargs):

        print('GradientTab.process', kwargs)

        # if no keyword, cache the fractal it is the one for the view
        cache = kwargs.pop('cache', len(kwargs) == 0)

        fractal = kwargs.pop('fractal', self.preproc_fractal)
        loop  = kwargs.pop('loop', self.loop)
        black_inside = kwargs.pop('black_inside', self.black_inside)

        if kwargs:
            print(f"Warning: GradientTab.process had unknown kwargs {tuple(kwargs.keys())}.")

        if fractal is None:
            print('Warning: GradientTab.process called without fractal.')
            return

        # grad = list(gradient('#0F4152', '#59A07B', '#F7E491', '#EDB825', '#EB3615', loop=loop))
        # grad = list(gradient('#7d451b', '#78bc61', '#e3d26f', '#e3d26f', loop=loop))
        # grad = list(gradient(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=loop))
        # grad = [hsv_to_RGB(h / 1000, 1 , 1) for h in range(1000)]
        # grad = list(gradient(*"39624D 63A26E C6B070 E47735 A62413".split(), loop=loop))
        # grad = list(gradient(*"FFD500 FFA500 864A29 000080 F2F2E9".split(), loop=loop))
        # grad = list(gradient(*"D83537 DD8151 F1DC81 7CCB86 4C5C77".split(), loop=loop))
        # grad = list(gradient(*"01ACD7 68C6C9 EFDC85 EB9821 9F290E".split(), loop=loop))
        # grad = list(gradient(*"000000 ff0000 000000 ffffff".split(), loop=loop))
        # grad = list(gradient(*"78ACDA 143986 0F1529 226197 8F82E2".split(), loop=loop))
        # grad = list(gradient(*"1F1D21 108D90 F5B33E FA7252 DA4D3F".split(), loop=loop))
        grad = list(gradient(*"10182D 080908 D0490C DCAF14 F7EE51".split(), loop=loop))
        # grad = list(gradient(*"236261 14A087 93CC9D FDC97E ED3533".split(), loop=loop))
        # grad = list(gradient(*"FAFAFA F0CA32 F3431B 67221B 0B0C0D".split(), loop=loop))

        if black_inside:
            image = apply_gradient(fractal, grad, inside=BLACK)
        else:
            image = apply_gradient(abs(fractal), grad)

        if cache:
            self.colored_fractal = image
        else:
            return image
