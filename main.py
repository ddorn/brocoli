#!/usr/bin/env python3
import os
from colorsys import hsv_to_rgb
from datetime import datetime
from os import path

from PIL import Image, ImageFilter
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivymd.app import MDApp

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
    preproc_tab : PreprocTab = ObjectProperty()
    gradient_tab : GradientTab = ObjectProperty()
    save_tab : SaveTab = ObjectProperty()

    image = ObjectProperty(None)  # type: KivyImage
    colored_fractal = ObjectProperty(force_dispatch=True, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_size(self, *args):
        self.camera_tab.on_view_size_change(self.size)

    def on_colored_fractal(self, *args):
        if self.colored_fractal is None:
            print("Brocoli.on_colored_fractal was called with no fractal")
            return
        
        image = Image.fromarray(self.colored_fractal.swapaxes(0, 1), mode='RGB')
        if self.camera_tab.pixel_size > 1:
            size = int(self.image.size[0]), int(self.image.size[1])
            image = image.resize(size)
        image.save("frac.png")
        self.image.source = "frac.png"
        self.image.reload()
        self.image.mag_filter = 'nearest'
        # self.image.texture.min_filter = 'nearest'
        print('updated !')


    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.camera_tab.camera.zoom(0.69, (touch.x, self.height - touch.y))
            return True

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
