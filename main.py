#!/usr/bin/env python3
from colorsys import hsv_to_rgb
from datetime import datetime
from os import path

import numpy as np
from PIL import Image
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget

from camera import SimpleCamera
from colorize import apply_gradient, normalize_quantiles
from colors import gradient
from compute import compute, random_position


def hsv_to_RGB(h, s, v):
    r, g, b = hsv_to_rgb(h, s, v)
    return int(255 * r), int(255 * g), int(255 * b)


class LabeledSlider(BoxLayout):
    min = NumericProperty()
    max = NumericProperty()
    default = NumericProperty()
    value = NumericProperty()
    text = StringProperty()
    step = NumericProperty()


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
    steps_power = NumericProperty(1)
    normalize_quantiles = BooleanProperty()

    fractal = ObjectProperty(force_dispatch=True)
    image = ObjectProperty(None)  # type: KivyImage

    coloring_change = ReferenceListProperty(loop_gradient,
                                            gradient_speed,
                                            gradient_offset,
                                            black_inside,
                                            steps_power,
                                            normalize_quantiles,
                                            fractal)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pause = False
        self._need_compute = False
        self.pause()

        # TODO: make it a property
        self.gradient = list(gradient(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=self.loop_gradient))
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

    def on_loop_gradient(self, *args):

        # grad = list(gradient('#0F4152', '#59A07B', '#F7E491', '#EDB825', '#EB3615', loop=self.loop_gradient))
        # grad = list(gradient('#7d451b', '#78bc61', '#e3d26f', '#e3d26f', loop=self.loop_gradient))
        # self.gradient = list(gradient(*"D3AD2B D02C22 223336 326C67 187C25".split(), loop=self.loop_gradient))
        # self.gradient = [hsv_to_RGB(h / 1000, 1 , 1) for h in range(1000)]
        # self.gradient = list(gradient(*"39624D 63A26E C6B070 E47735 A62413".split(), loop=self.loop_gradient))
        # self.gradient = list(gradient(*"39624D 63A26E CABF40 FFCB00 F25615".split(), loop=self.loop_gradient))
        # self.gradient = list(gradient(*"FFD500 FFA500 864A29 000080 F2F2E9".split(), loop=self.loop_gradient))
        self.gradient = list(gradient(*"D83537 DD8151 F1DC81 7CCB86 4C5C77".split(), loop=self.loop_gradient))

    def recompute(self):
        if self._pause:
            self._need_compute = True
            return

        print("Computing fractal", self.camera, "steps:", self.steps)
        self.fractal = compute(self.camera, self.steps, self.kind)
        print("done.")

    def on_coloring_change(self, *args):
        if self.fractal is None:
            return

        fractal = self.fractal

        if self.normalize_quantiles:
            fractal = normalize_quantiles(fractal, len(self.gradient))

        image = apply_gradient(fractal ** self.steps_power, self.gradient, self.gradient_speed, self.gradient_offset)

        if self.black_inside and self.kind in (0, 1):
            image[self.fractal >= self.steps] = (0, 0, 0)

        self.update_image(image)

    def save_4k(self):
        def4k = 3840, 2160

        # Compute with high resolution
        camera = SimpleCamera(def4k, self.camera.center, self.camera.height)
        print(f"Computing {def4k[0]}x{def4k[1]} fractal")
        fractal = raw = compute(camera, self.steps, self.kind)

        # Color the fractal
        if self.normalize_quantiles:
            print("Normalizing quantiles...")
            fractal = normalize_quantiles(fractal, len(self.gradient))
        print("Applying gradient...")
        image = apply_gradient(fractal ** self.steps_power, self.gradient, self.gradient_speed, self.gradient_offset)
        if self.black_inside and self.kind in (0, 1):
            print("Setting center black...")
            image[raw >= self.steps] = (0, 0, 0)

        # Saving with a unique name
        image = Image.fromarray(image.swapaxes(0, 1), mode='RGB')
        name = datetime.now().strftime("%Y-%m-%d %Hh%Mm%S fractal 4k.png")
        print(f"Saving as {name}...")
        image.save(path.join('out', name))
        print("Done !")

    def update_image(self, image):
        """
        Update brocoli's displayed image given an ndarray of
        size (height, width, 3) of int8 representing colors.
        """

        image = Image.fromarray(image.swapaxes(0, 1), mode='RGB')
        if self.pixel_size != 1:
            image = image.resize(self.int_size)

        image.save("frac.png")
        self.image.source = "frac.png"
        self.image.reload()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.camera.zoom(0.69, (touch.x, self.height - touch.y))
            return True

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
