#!/usr/bin/env python3
import os
from colorsys import hsv_to_rgb

from PIL import Image
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivymd.app import MDApp

from compute import Coloration
from random_fractal import random_fractal, random_position, optimal_limit, random_kind, random_gradient
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

class LogLabeledSlider(BoxLayout):
    min = NumericProperty()
    max = NumericProperty()
    default = NumericProperty()
    value = NumericProperty()
    text = StringProperty()
    step = NumericProperty()


class Brocoli(Widget):
    # Tabs
    camera_tab: CameraTab = ObjectProperty()
    preproc_tab: PreprocTab = ObjectProperty()
    gradient_tab: GradientTab = ObjectProperty()
    save_tab: SaveTab = ObjectProperty()

    image = ObjectProperty(None)  # type: KivyImage
    colored_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def on_size(self, *args):
        self.camera_tab.on_view_size_change(self.size)

    def update_image_from_array(self, fractal):
        image = Image.fromarray(fractal.swapaxes(0, 1), mode='RGB')
        if image.size != self.int_size:
            image = image.resize(self.int_size)
        image.save("frac.png")
        self.image.source = "frac.png"
        self.image.reload()

    def on_colored_fractal(self, *args):
        if self.colored_fractal is None:
            print("Brocoli.on_colored_fractal was called with no fractal")
            return

        self.update_image_from_array(self.colored_fractal)
        print('updated !')

    def random_fractal(self, *args):
        with self.gradient_tab:
            with self.preproc_tab:
                with self.camera_tab:
                    camera = random_position()
                    self.camera_tab.set_camera_pov(camera.center, camera.height)
                    self.camera_tab.steps = optimal_limit(camera)
                    self.camera_tab.kind = random_kind()
                self.preproc_tab.speed = 2
                self.preproc_tab.offset = 0
                self.preproc_tab.normalize_quantiles = self.camera_tab.kind == Coloration.SMOOTH_TIME
            self.gradient_tab.gradient = random_gradient()
            self.gradient_tab.black_inside = False
        print('Randomly updated !')

    def on_touch_down(self, touch):
        if super(Brocoli, self).on_touch_down(touch):
            return True

        if self.collide_point(touch.x, touch.y):
            self.camera_tab.camera.zoom(0.69, (touch.x, self.height - touch.y))
            return True

    @property
    def int_size(self):
        return int(self.size[0]), int(self.size[1])

class MainWidget(Widget):
    pass


class BrocoliApp(MDApp):

    def __init__(self, **kwargs):

        for kv in os.listdir('./tabs'):
            if kv.endswith('.kv'):
                print("Loaded", kv)
                Builder.load_file(os.path.join('tabs', kv))
        self.title = "Brocoli"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"

        super().__init__(**kwargs)

    def build(self):
        return MainWidget()


if __name__ == '__main__':
    BrocoliApp().run()
