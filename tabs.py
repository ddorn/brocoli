from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, ReferenceListProperty, AliasProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.tab import MDTabsBase

from camera import SimpleCamera
from colors import gradient
from compute import random_position
from dispatcher_extension import EventDispatcherExtension

__all__ = ['MyTab', 'CameraTab', 'GradientTab', 'SaveTab']

class MyTab(BoxLayout, MDTabsBase, EventDispatcherExtension):
    brocoli = ObjectProperty(rebind=True)



class CameraTab(MyTab):
    kind = NumericProperty(3)
    pixel_size = NumericProperty()
    steps = NumericProperty()
    camera = ObjectProperty(SimpleCamera((1, 1)), rebind=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_components_for_change("pixel_size kind steps camera".split())
        self.camera.bind(on_change=self.dispatch_change)

    def on_steps(self, *args):
        print("STEPS", args)

    def on_view_size_change(self, new_size):
        self.camera.size = int(new_size[0] / self.pixel_size), int(new_size[1] / self.pixel_size)

    def set_random_position(self, *args):
        new_camera = random_position()

        with self:
            self.camera.center = new_camera.center
            self.camera.height = new_camera.height

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



class SaveTab(MyTab):
    pass