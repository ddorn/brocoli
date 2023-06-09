from dataclasses import dataclass
from typing import List, Union, Tuple

import yaml
from PIL import Image

from .processing.camera import SimpleCamera
from .processing.colorize import colorize
from .processing.colors import to_hex
from .processing.compute import Coloration, compute
from .processing.preprocess import preprocess

Color = Tuple[int, int, int]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


@dataclass
class Fractal(yaml.YAMLObject):
    # View
    camera: SimpleCamera
    kind: Coloration = Coloration.SMOOTH_TIME
    limit: int = 128
    bound: int = 20_000
    julia: Union[None, complex] = None
    # pre-processing
    normalize_quantiles: bool = False
    steps_power: float = 1.0
    bins: int = 1
    # Colors
    gradient_points: List[Color] = (BLACK, WHITE)
    color_count: int = 1000
    gradient_loop: bool = False
    gradient_speed: float = 1.0
    gradient_offset: float = 0.0
    inside_color: Union[None, Color] = None

    # Infos
    seed: str = None
    # For Yaml loading
    yaml_tag = "Fractal"

    def render(self, as_pillow_image=False):
        fractal = compute(
            self.camera, self.kind, limit=self.limit, bound=self.bound, julia=self.julia
        )
        fractal = preprocess(fractal, self.bins, self.normalize_quantiles, self.steps_power)
        fractal = colorize(
            fractal,
            self.gradient_points,
            speed=self.gradient_speed,
            offset=self.gradient_offset,
            inside_color=self.inside_color,
            color_count=self.color_count,
            loop=self.gradient_loop,
        )

        fractal = fractal.swapaxes(0, 1)

        if as_pillow_image:
            return Image.fromarray(fractal, mode="RGB")
        else:
            return fractal

    def as_dict(self):
        return dict(
            center=self.camera.center,
            height=self.camera.height,
            size=self.camera.size,
            kind=self.kind,
            limit=self.limit,
            bound=self.bound,
            julia=self.julia,
            normalize_quantiles=self.normalize_quantiles,
            steps_power=self.steps_power,
            bins=self.bins,
            gradient_points=[to_hex(c) for c in self.gradient_points],
            color_count=self.color_count,
            gradient_loop=self.gradient_loop,  # can set with gradient_points
            gradient_speed=self.gradient_speed,
            gradient_offset=self.gradient_offset,
            inside_color=self.inside_color,
        )


if __name__ == "__main__":

    cam = SimpleCamera((1920, 1080))
    f = Fractal(
        cam, gradient_loop=True, normalize_quantiles=True, inside_color=(255, 169, 0)
    )
    i = f.render()

    i = Image.fromarray(i, mode="RGB")
    i.show()
