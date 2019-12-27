from kivy.event import EventDispatcher


class EventDispatcherExtension(EventDispatcher):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pause = 0
        self._need_dispatch = False
        self.register_event_type('on_change')

    def set_components_for_change(self, compl: list):
        # return NotImplemented
        self.bind(**{name: self.dispatch_change for name in compl})

    def on_change(self, *args):
        pass

    def dispatch_change(self, *args):
        if self._pause:
            self._need_dispatch = True
            return

        # print("dispatch change", self, args)
        # print(self, "CHAAAANGE", args)
        self.dispatch('on_change')

    def __enter__(self):
        self._pause += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pause -= 1
        if not self._pause and self._need_dispatch:
            self.dispatch_change("on resume")
            self._need_dispatch = False