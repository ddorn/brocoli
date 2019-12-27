from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ReferenceListProperty, ObjectProperty

from processing.colorize import normalize_quantiles, signed_normalize_ip, signed_power
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

        self.set_components_for_change('speed offset steps_power normalize_quantiles fractal'.split())
        self.bind(on_change=self.process)
        def f(*a): self.steps_power = 1
        Clock.schedule_once(f, 0)

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
            fractal = signed_power(fractal, steps_power)

        # put fractal between -1 and 1
        signed_normalize_ip(fractal, speed, offset)

        if cache:
            self.preproc_fractal = fractal
        else:
            return fractal