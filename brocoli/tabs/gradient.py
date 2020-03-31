from kivy.clock import Clock
from kivy.properties import (
    ObjectProperty,
    BooleanProperty,
    ReferenceListProperty,
    NumericProperty,
)

from ..processing.colorize import colorize
from ..processing.colors import gradient, BLACK
from .base import MyTab


class GradientTab(MyTab):
    loop = BooleanProperty(True)
    black_inside = BooleanProperty(True)
    gradient = ObjectProperty()
    speed = NumericProperty(1)
    offset = NumericProperty(0)

    any = ReferenceListProperty(gradient, speed, offset, black_inside)

    preproc_fractal = ObjectProperty(force_dispatch=True, allownone=True)
    colored_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        loop = True
        grad = list(
            gradient("#0F4152", "#59A07B", "#F7E491", "#EDB825", "#EB3615", loop=True)
        )
        # grad = list(gradient(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=loop))
        # grad = [hsv_to_RGB(h / 1000, 1 , 1) for h in range(1000)]
        # grad = list(gradient(*"39624D 63A26E C6B070 E47735 A62413".split(), loop=loop))
        # grad = list(gradient(*"D83537 DD8151 F1DC81 7CCB86 4C5C77".split(), loop=loop))
        # grad = list(gradient(*"01ACD7 68C6C9 EFDC85 EB9821 9F290E".split(), loop=loop))
        # grad = list(gradient(*"000000 ff0000 000000 ffffff".split(), loop=loop))
        # grad = list(gradient(*"78ACDA 143986 0F1529 226197 8F82E2".split(), loop=loop))
        # grad = list(gradient(*"1F1D21 108D90 F5B33E FA7252 DA4D3F".split(), loop=loop))
        # grad = list(gradient(*"10182D 080908 D0490C DCAF14 F7EE51".split(), loop=loop))
        # grad = list(gradient(*"236261 14A087 93CC9D FDC97E ED3533".split(), loop=loop))
        # grad = list(gradient(*"FAFAFA F0CA32 F3431B 67221B 0B0C0D".split(), loop=loop))
        # grad = list(gradient(*"0E0E0E 40160E C7341B E78F2A F6F5F2".split(), loop=loop))
        # grad = list(gradient(*"244D5D 10A8D6 DCCDC1 C7794A CC4B3D".split(), loop=loop))
        # grad = list(gradient(*"073D52 10A8D6 F2E8DA F2903A B94C23".split(), loop=loop))
        # grad = list(gradient(*"05435F 099086 71D280 EFE84D F4B842".split(), loop=loop))
        self.gradient = grad

        Clock.schedule_once(self.do_binds)

    def do_binds(self, *args):
        self.set_components_for_change("any preproc_fractal".split())
        self.bind(on_change=self.process)

    def process(self, *args, **kwargs):

        print("GradientTab.process", kwargs)

        # if no keyword, cache the fractal it is the one for the view
        cache = kwargs.pop("cache", len(kwargs) == 0)

        fractal = kwargs.pop("fractal", self.preproc_fractal)
        # loop = kwargs.pop('loop', self.loop)
        gradient = kwargs.pop("gradient", self.gradient)
        speed = kwargs.pop("speed", self.speed)
        offset = kwargs.pop("offset", self.offset)
        black_inside = kwargs.pop("black_inside", self.black_inside)

        inside_color = BLACK if black_inside else None

        if kwargs:
            print(
                f"Warning: GradientTab.process had unknown kwargs {tuple(kwargs.keys())}."
            )

        if fractal is None:
            print("Warning: GradientTab.process called without fractal.")
            return

        image = colorize(
            fractal,
            gradient,
            speed=speed,
            offset=offset,
            inside_color=inside_color,
            color_count=1000,  # TODO: slider for color count
        )

        if cache:
            self.colored_fractal = image
        else:
            return image
