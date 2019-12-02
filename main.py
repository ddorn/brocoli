#!/usr/bin/env python3


import numpy as np
from PIL import Image
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget

from camera import SimpleCamera
from colorize import apply_gradient
from colors import gradient
from compute import compute, random_position


class Brocoli(Widget):
    # Camera
    camera = SimpleCamera((10, 10), -0.75, 2)
    steps = NumericProperty(50)
    pixel_size = NumericProperty(3)
    # Draw
    kind = NumericProperty(3)
    loop_gradient = BooleanProperty(False)
    gradient_speed = NumericProperty(1)
    gradient_offset = NumericProperty(0)
    black_inside = BooleanProperty(True)
    smooth_high_steps = NumericProperty(1)

    fractal = ObjectProperty(force_dispatch=True)
    image = ObjectProperty(None)  # type: KivyImage

    coloring_change = ReferenceListProperty(loop_gradient,
                                            gradient_speed,
                                            gradient_offset,
                                            black_inside,
                                            smooth_high_steps,
                                            fractal)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pause = False
        self._need_compute = False
        self.pause()

        self.camera.bind(any=self.on_camera)
        self.bind(steps=self.on_camera, kind=self.on_camera)
        self.bind(pixel_size=self.on_size)

        self.resume()

    @property
    def int_size(self):
        return int(self.size[0]), int(self.size[1])

    def on_size(self, *args):
        self.camera.size = int(self.size[0] / self.pixel_size), int(self.size[1] / self.pixel_size)

    def on_camera(self, *args):
        self.recompute()

    def recompute(self):
        if self._pause:
            self._need_compute = True
            return

        surf = np.empty(self.camera.size)

        print("Computing fractal", self.camera, "steps:", self.steps)
        compute(surf, self.camera.bottomleft, self.camera.step, self.steps, self.kind)
        print("done.")

        self.fractal = surf

    def get_smoothed_high_steps(self):
        if not self.smooth_high_steps:
            return self.fractal

        maxi = np.nanmax(self.fractal)
        mini = np.nanmin(self.fractal)
        threshold = self.smooth_high_steps * (maxi - mini) + mini
        high = self.fractal > threshold
        fractal = self.fractal.copy()
        fractal[high] = np.sqrt(fractal[high] - threshold) + threshold
        fractal[0,0] = maxi
        return fractal

    def on_coloring_change(self, *args):
        if self.fractal is None:
            return

        fractal = self.get_smoothed_high_steps()  # if needed

        # grad = list(gradient('#0F4152', '#59A07B', '#F7E491', '#EDB825', '#EB3615', loop=self.loop_gradient))
        # grad = list(gradient('#7d451b', '#78bc61', '#e3d26f', '#e3d26f', loop=self.loop_gradient))
        grad = list(gradient(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=self.loop_gradient))

        image = apply_gradient(fractal, grad, self.gradient_speed, self.gradient_offset)

        if self.black_inside:
            image[self.fractal >= self.steps] = (0, 0, 0)

        image = Image.fromarray(image.swapaxes(0, 1), mode='RGB')
        if self.pixel_size != 1:
            image = image.resize(self.int_size)

        image.save("frac.png")
        self.image.source = "frac.png"
        self.image.reload()

    def on_touch_down(self, touch):
        self.camera.zoom(0.69, (touch.x, self.height - touch.y))

    def set_random_position(self, *args):
        self.pause()
        new_camera = random_position()
        self.camera.center = new_camera.center
        self.camera.height = new_camera.height
        self.resume()

    def pause(self):
        """
        Pause fractal computing and drawing until resume is called.

        Useful to change multiple parameters at once without computing the fractal at each step.
        """

        self._pause = True

    def resume(self):
        self._pause = False
        if self._need_compute:
            self.recompute()

class MainWidget(Widget):
    pass


class BrocoliApp(App):
    def build(self):
        return MainWidget()

if __name__ == '__main__':
    BrocoliApp().run()
