from kivy.clock import Clock
from kivy.properties import (
    NumericProperty,
    BooleanProperty,
    ReferenceListProperty,
    ObjectProperty,
)

from ..processing.preprocess import preprocess
from .base import MyTab


class PreprocTab(MyTab):
    bins = NumericProperty(1)
    steps_power = NumericProperty(1)
    normalize_quantiles = BooleanProperty()

    any = ReferenceListProperty(bins, steps_power, normalize_quantiles)

    fractal = ObjectProperty(force_dispatch=True, allownone=True)
    preproc_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_components_for_change("any fractal".split())
        self.bind(on_change=self.process)

        def f(*a):
            self.steps_power = 1

        Clock.schedule_once(f, 0)

    def process(self, *args, **kwargs):

        print("PreprocTab.process", kwargs)

        # if no keyword, cache the fractal it is the one for the view
        cache = kwargs.pop("cache", len(kwargs) == 0)
        fractal = kwargs.pop("fractal", self.fractal)
        bins = kwargs.pop("bins", self.bins)
        norm_quantiles = kwargs.pop("normalize_quantiles", self.normalize_quantiles)
        steps_power = kwargs.pop("steps_power", self.steps_power)

        if kwargs:
            print(
                f"Warning: GradientTab.process had unknown kwargs {tuple(kwargs.keys())}."
            )

        if fractal is None:
            print("Warning: GradientTab.process called without fractal.")
            return

        fractal = fractal.copy()

        fractal = preprocess(
                fractal,
                bins=bins,
                norm_quantiles=norm_quantiles,
                steps_power=steps_power
            )

        if cache:
            self.preproc_fractal = fractal
        else:
            return fractal
