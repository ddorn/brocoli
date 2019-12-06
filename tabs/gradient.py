from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, ReferenceListProperty

from colors import gradient
from tabs.base import MyTab


class GradientTab(MyTab):
    loop_gradient = BooleanProperty(True)
    gradient_speed = NumericProperty(1)
    gradient_offset = NumericProperty(0)
    black_inside = BooleanProperty(True)
    steps_power = NumericProperty(1)
    normalize_quantiles = BooleanProperty()

    any = ReferenceListProperty(loop_gradient,
                                gradient_speed,
                                gradient_offset,
                                black_inside,
                                steps_power,
                                normalize_quantiles)

    gradient = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(any=self.dispatch_change)

    def on_loop_gradient(self, *args):

        self.gradient = list(gradient('#0F4152', '#59A07B', '#F7E491', '#EDB825', '#EB3615', loop=self.loop_gradient))
        # grad = list(gradient('#7d451b', '#78bc61', '#e3d26f', '#e3d26f', loop=self.loop_gradient))
        # self.gradient = list(gradient(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=self.loop_gradient))
        # self.gradient = [hsv_to_RGB(h / 1000, 1 , 1) for h in range(1000)]
        # self.gradient = list(gradient(*"39624D 63A26E C6B070 E47735 A62413".split(), loop=self.loop_gradient))
        # self.gradient = list(gradient(*"FFD500 FFA500 864A29 000080 F2F2E9".split(), loop=self.loop_gradient))
        # self.gradient = list(gradient(*"D83537 DD8151 F1DC81 7CCB86 4C5C77".split(), loop=self.loop_gradient))
        # self.gradient = list(gradient(*"01ACD7 68C6C9 EFDC85 EB9821 9F290E".split(), loop=self.loop_gradient))

