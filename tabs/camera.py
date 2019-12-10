from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty

from camera import SimpleCamera
from compute import random_position, compute
from tabs.base import MyTab


class CameraTab(MyTab):
    kind = NumericProperty(1)
    pixel_size = NumericProperty()
    steps = NumericProperty(42)
    bound = NumericProperty(10)
    camera = ObjectProperty(SimpleCamera((42, 42), -0.75, 3), rebind=True)
    fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.process()
        Clock.schedule_once(self.do_binds)

    # def on_kind(self, *args):
    #     self.process()

    def do_binds(self, *args):
        self.set_components_for_change("pixel_size kind steps camera".split())
        self.camera.bind(on_change=self.process)
        self.bind(on_change=self.process)

    def process(self, *args, **kwargs):
        """
        Compute the mandelbrot defined by the tab.

        Any keyword argument overrides the value set by the tab.

        :steps: max number of steps to compute the fractal for
        :kind: type of coloration method
        :bound: bound where the sequence is divergent
        :camera: override the camera
        :height: override camera.height
        :center: override camera.center
        :size: override camera.size
        :return: ndarray of the computed mandelbrot
        """

        print('CameraTab.process', kwargs)

        # if no keyword, cache the fractal it is the one for the view
        cache = kwargs.pop('cache', len(kwargs) == 0)

        steps = kwargs.pop('steps', self.steps)
        kind = kwargs.pop('kind', self.kind)
        bound = kwargs.pop('bound', self.bound)
        camera = kwargs.pop('camera', self.camera)
        size = kwargs.pop('size', camera.size)
        height = kwargs.pop('height', camera.height)
        center = kwargs.pop('center', camera.center)
        camera = SimpleCamera(size, center, height)

        if kwargs:
            print(f"Warning: CameraTab had unknown kwargs {tuple(kwargs.keys())}.")

        print("Computing fractal", camera, "steps:", steps)
        fractal = compute(camera, steps, kind)

        if cache:
            self.fractal = fractal
        else:
            return fractal

    def on_view_size_change(self, new_size):
        self.camera.size = int(new_size[0] / self.pixel_size), int(new_size[1] / self.pixel_size)

    def set_random_position(self, *args):
        new_camera = random_position()

        with self.camera:
            self.camera.center = new_camera.center
            self.camera.height = new_camera.height
