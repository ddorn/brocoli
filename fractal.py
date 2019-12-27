from dataclasses import dataclass
from typing import List, Union, Tuple

from processing.camera import SimpleCamera
from processing.colorize import colorize
from processing.compute import Coloration, compute
from processing.preprocess import preprocess

Color = Tuple[int, int, int]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

@dataclass
class Fractal:
    # View
    camera: SimpleCamera
    kind: Coloration = Coloration.SMOOTH_TIME
    limit: int = 128
    bound: int = 20_000
    julia: Union[None, complex] = None
    # pre-processing
    normalize_quantiles: bool = False
    steps_power = 1.0
    # Colors
    gradient_points: List[Color] = (BLACK, WHITE)
    color_count = 1000
    gradient_loop: bool = False
    gradient_speed: float = 1.
    gradient_offset: float = 0.
    inside_color: Union[None, Color] = BLACK

    def render(self):
        fractal = compute(self.camera, self.kind, limit=self.limit, bound=self.bound, julia=self.julia)
        fractal = preprocess(fractal, self.normalize_quantiles, self.steps_power)
        fractal = colorize(fractal, self.gradient_points,
                           speed=self.gradient_speed,
                           offset=self.gradient_offset,
                           inside_color=self.inside_color,
                           color_count=self.color_count,
                           loop=self.gradient_loop,
                           )

        return fractal.swapaxes(0, 1)

if __name__ == '__main__':
    cam = SimpleCamera((1920, 1080))
    f = Fractal(cam, gradient_loop=True, normalize_quantiles=True, inside_color=(255, 169, 0))
    i = f.render()
    from PIL import Image
    i = Image.fromarray(i, mode='RGB')
    i.show()