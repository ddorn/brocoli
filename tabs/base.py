from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.tab import MDTabsBase

from dispatcher_extension import EventDispatcherExtension


class MyTab(BoxLayout, MDTabsBase, EventDispatcherExtension):
    brocoli = ObjectProperty(rebind=True)
