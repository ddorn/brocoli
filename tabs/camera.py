from kivy.properties import ObjectProperty, NumericProperty

from camera import SimpleCamera
from compute import random_position
from tabs.base import MyTab


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
