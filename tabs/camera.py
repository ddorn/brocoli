from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, OptionProperty, BooleanProperty, ReferenceListProperty

from camera import SimpleCamera
from compute import compute, Coloration
from dispatcher_extension import EventDispatcherExtension
from random_fractal import random_position
from tabs.base import MyTab


class EventDispatcherCamera(SimpleCamera, EventDispatcherExtension):
    center = ObjectProperty(0j)
    height = NumericProperty(2)
    w = NumericProperty()
    h = NumericProperty()
    size = ReferenceListProperty(w, h)

    def __init__(self, size, *args, **kwargs):
        super().__init__(size, *args, **kwargs)

        self.bind(center=self.dispatch_change,
                  height=self.dispatch_change,
                  size=self.dispatch_change)


class CameraTab(MyTab):
    kind = OptionProperty(Coloration.AVG_TRIANGLE_INEQUALITY, options=list(Coloration))
    pixel_size = NumericProperty()
    steps = NumericProperty(42)
    bound = NumericProperty(10)
    camera : EventDispatcherCamera = ObjectProperty(EventDispatcherCamera((42, 42), -0.75, 3), rebind=True)
    fractal = ObjectProperty(force_dispatch=True, allownone=True)
    julia_active = BooleanProperty(False)
    julia_c = ObjectProperty(0j)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saved_camera = SimpleCamera((2, 2))

        self.kind_items = [
            {
                "viewclass": "MDMenuItem",
                "text": col.value,
                "callback": self.set_kind,
            }
            for col in Coloration
        ]
        # self.process()
        Clock.schedule_once(self.finish_init)

    def set_kind(self, kind, *args):
        self.kind = Coloration(kind)

    def set_camera_pov(self, center, height):
        with self.camera:
            self.camera.center = center
            self.camera.height = height

    def on_julia_active(self, sender, julia):
        if julia:
            self.saved_camera = SimpleCamera(self.camera.size, self.camera.center, self.camera.height)
            self.julia_c = self.camera.center

            self.set_camera_pov(0j, 3)
        else:
            self.set_camera_pov(self.saved_camera.center, self.saved_camera.height)



    def finish_init(self, *args):
        self.bound = 20_000
        self.steps = 256

        self.set_components_for_change("pixel_size kind bound julia_c julia_active steps camera".split())
        self.camera.bind(on_change=self.dispatch_change)
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

        pixel_size = kwargs.pop('pixel_size', self.pixel_size)
        steps = kwargs.pop('steps', self.steps)
        kind = kwargs.pop('kind', self.kind)
        bound = kwargs.pop('bound', self.bound)
        julia_active = kwargs.pop('julia_active', self.julia_active)
        julia_c = kwargs.pop('julia_c', self.julia_c) if julia_active else None
        camera = kwargs.pop('camera', self.camera)
        size = kwargs.pop('size', camera.size)
        height = kwargs.pop('height', camera.height)
        center = kwargs.pop('center', camera.center)
        real_size = size[0] // pixel_size, size[1] // pixel_size
        camera = SimpleCamera(real_size, center, height)

        if kwargs:
            print(f"Warning: CameraTab had unknown kwargs {tuple(kwargs.keys())}.")

        print("Computing fractal", camera, "steps:", steps)
        fractal = compute(camera, kind, limit=steps, bound=bound, julia=julia_c)

        if cache:
            self.fractal = fractal
        else:
            return fractal

    def on_view_size_change(self, new_size):
        self.camera.size = int(new_size[0]), int(new_size[1])

    def set_camera_center(self, text):
        try:
            self.camera.center = complex(text)
            return True
        except ValueError:
            print(f"{text} is not a valid complex")

    def set_random_position(self, *args):
        new_camera = random_position()

        if self.julia_active:
            self.saved_camera.center = new_camera.center
            self.saved_camera.height = new_camera.height
            self.julia_c = new_camera.center
        else:
            with self.camera:
                self.camera.center = new_camera.center
                self.camera.height = new_camera.height
