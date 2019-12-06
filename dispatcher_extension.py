from kivy.event import EventDispatcher
from kivy.properties import ReferenceListProperty


class EventDispatcherExtension(EventDispatcher):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pause = False
        self._need_dispatch = False
        self.register_event_type('on_change')

    def set_components_for_change(self, compl: list):
        self.bind(**{name: self.dispatch_change for name in compl})

    def on_change(self, *args):
        pass

    def dispatch_change(self, *args):
        if self._pause:
            self._need_dispatch = True
            return

        print("dispatch change", self, args)
        self.dispatch('on_change', args)

    def __enter__(self):
        self._pause = True
        self._need_dispatch = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pause = False
        if self._need_dispatch:
            self.dispatch_change("on resume")
            self._need_dispatch = False