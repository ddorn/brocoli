from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.tab import MDTabsBase

from tabs.dispatcher_extension import EventDispatcherExtension

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kivymain import Brocoli


class MyTab(BoxLayout, MDTabsBase, EventDispatcherExtension):
    brocoli = ObjectProperty(rebind=True)  # type: Brocoli

    def process(self, *args, **kwargs):
        return NotImplemented
