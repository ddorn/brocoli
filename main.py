#!/usr/bin/env python3
from colorsys import hsv_to_rgb
from datetime import datetime
from os import path

from PIL import Image
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty, ReferenceListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivymd.app import MDApp

from camera import SimpleCamera
from colorize import apply_gradient, normalize_quantiles
from colors import gradient
from compute import compute, random_position
from tabs import *


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
    # Tabs
    camera_tab : CameraTab = ObjectProperty()
    gradient_tab : GradientTab = ObjectProperty()
    post_processing_tab = ObjectProperty()
    save_tab : SaveTab = ObjectProperty()

    fractal = ObjectProperty(force_dispatch=True)
    image = ObjectProperty(None)  # type: KivyImage

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.do_binds)

    def do_binds(self, *args):
        self.camera_tab.bind(on_change=self.on_camera)
        self.gradient_tab.bind(on_change=self.recolor)
        self.bind(fractal=self.recolor)

    @property
    def int_size(self):
        return int(self.size[0]), int(self.size[1])

    def on_size(self, *args):
        self.camera_tab.on_view_size_change(self.size)

    def on_camera(self, *args):
        print("ON CAMERA", *args)
        self.recompute()

    def recompute(self):

        print("Computing fractal", self.camera_tab.camera, "steps:", self.camera_tab.steps)
        self.fractal = compute(self.camera_tab.camera, self.camera_tab.steps, self.camera_tab.kind)
        print("done.")

    def recolor(self, *args):
        if self.fractal is None:
            return

        fractal = self.fractal

        if self.gradient_tab.normalize_quantiles:
            fractal = normalize_quantiles(fractal, len(self.gradient))

        image = apply_gradient(fractal ** self.gradient_tab.steps_power, self.gradient, self.gradient_tab.gradient_speed, self.gradient_tab.gradient_offset)

        if self.gradient_tab.black_inside and self.camera_tab.kind in (0, 1):
            image[self.fractal >= self.camera_tab.steps] = (0, 0, 0)

        self.update_image(image)

    def save_4k(self):
        def4k = 3840, 2160

        # Compute with high resolution
        camera = SimpleCamera(def4k, self.camera_tab.camera.center, self.camera_tab.camera.height)
        print(f"Computing {def4k[0]}x{def4k[1]} fractal")
        fractal = raw = compute(camera, self.camera_tab.steps, self.camera_tab.kind)

        # Color the fractal
        if self.gradient_tab.normalize_quantiles:
            print("Normalizing quantiles...")
            fractal = normalize_quantiles(fractal, len(self.gradient))
        print("Applying gradient...")
        image = apply_gradient(fractal ** self.gradient_tab.steps_power, self.gradient, self.gradient_tab.gradient_speed, self.gradient_tab.gradient_offset)
        if self.gradient_tab.black_inside and self.camera_tab.kind in (0, 1):
            print("Setting center black...")
            image[raw >= self.camera_tab.steps] = (0, 0, 0)

        # Saving with a unique name
        image = Image.fromarray(image.swapaxes(0, 1), mode='RGB')
        name = datetime.now().strftime("%Y-%m-%d %Hh%Mm%S fractal 4k.png")
        print(f"Saving as {name}...")
        image.save(path.join('out', name))
        print("Done !")

    @property
    def gradient(self):
        return self.gradient_tab.gradient

    def update_image(self, image):
        """
        Update brocoli's displayed image given an ndarray of
        size (height, width, 3) of int8 representing colors.
        """

        image = Image.fromarray(image.swapaxes(0, 1), mode='RGB')
        if self.camera_tab.pixel_size != 1:
            image = image.resize(self.int_size)

        image.save("frac.png")
        self.image.source = "frac.png"
        self.image.reload()
        print('updated !')

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.camera_tab.camera.zoom(0.69, (touch.x, self.height - touch.y))
            return True

class MainWidget(Widget):
    pass


class BrocoliApp(MDApp):

    def __init__(self, **kwargs):
        self.title = "Brocoli"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        super().__init__(**kwargs)

    def build(self):
        return MainWidget()

if __name__ == '__main__':
    BrocoliApp().run()
