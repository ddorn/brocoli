import os
from datetime import datetime

from PIL import Image
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.chip import MDChip

from tabs.base import MyTab


class ResoChip(MDChip):
    res = ListProperty((100, 100))

class SaveTab(MyTab):
    DEF4K = (3840, 2160)
    resolution = ObjectProperty(DEF4K)
    RESOLUTIONS = (DEF4K,
                   (1920, 1080),
                   (1920, 1080),
                   (1366, 768),
                   (1280, 720),
                   )

    choose_chip = ObjectProperty()
    colored_fractal = ObjectProperty(force_dispatch=True, allownone=True)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build)

    def build(self, *args):
        def callback(res):
            def f(*args):
                self.resolution = res
            return f

        for res in self.RESOLUTIONS:
            self.choose_chip.add_widget(ResoChip(res=res,
                                                 callback=callback(res)))

    def save(self, *args):

        fractal = self.brocoli.camera_tab.process(size=self.resolution, pixel_size=1)
        preproc_fractal = self.brocoli.preproc_tab.process(fractal=fractal)
        colored_fractal = self.brocoli.gradient_tab.process(fractal=preproc_fractal)

        # Saving with a unique name
        image = Image.fromarray(colored_fractal.swapaxes(0, 1), mode='RGB')
        name = datetime.now().strftime("%Y-%m-%d %Hh%Mm%S fractal 4k.png")
        print(f"Saving as out/{name}...")
        image.save(os.path.join('out', name))
        print("Done !")