from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty


class SimpleCamera(EventDispatcher):
    center = ObjectProperty(0j)
    height = NumericProperty(2)
    w = NumericProperty()
    h = NumericProperty()
    size = ReferenceListProperty(w, h)

    any = ReferenceListProperty(center, height, size)

    def __init__(self, size, center=0j, height=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.center = center
        self.height = height
        self.size = size

    @property
    def step(self):
        return self.width / self.size[0]

    @property
    def complex_size(self):
        return complex(self.width, self.height)

    @property
    def width(self):
        return self.height * self.size[0] / self.size[1]

    @property
    def bottomleft(self):
        return self.center - self.complex_size / 2

    def complex_at(self, pixel):
        return self.bottomleft + self.step * complex(pixel[0], (self.size[1] - pixel[1]))

    def zoom(self, zoom, pixel):
        before = self.complex_at(pixel)
        self.height *= zoom
        self.fix(pixel, before)

    def fix(self, pixel, c):
        self.center -= self.complex_at(pixel) - c

    def pixel_at(self, complex):
        cpixel = (complex - self.bottomleft) / self.step
        return round(cpixel.real), round(self.size[1] - cpixel.imag)