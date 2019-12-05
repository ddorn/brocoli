from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivymd.uix.tab import MDTabsBase


class MyTab(BoxLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_widget(self, widget: Widget, index=0, canvas=None):
        super(MyTab, self).add_widget(widget, index, canvas)

