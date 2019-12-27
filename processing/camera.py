class SimpleCamera:
    def __init__(self, size, center=0j, height=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.center = center
        self.height = height
        self.size = size

        # self.set_components_for_change("center height size".split())

    def __repr__(self) -> str:
        return f"<Camera({self.size[0]}x{self.size[1]}, {float(self.height) :.2}, {self.center})>"

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
        return self.bottomleft + self.step * complex(
            pixel[0], (self.size[1] - pixel[1])
        )

    def zoom(self, zoom, pixel):
        before = self.complex_at(pixel)
        with self:
            self.height *= zoom
            self.fix(pixel, before)

    def fix(self, pixel, c):
        self.center -= self.complex_at(pixel) - c

    def pixel_at(self, complex):
        cpixel = (complex - self.bottomleft) / self.step
        return round(cpixel.real), round(self.size[1] - cpixel.imag)
