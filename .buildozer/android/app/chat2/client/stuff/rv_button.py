from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors.focus import FocusBehavior

class RecycleBoxLayout22(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class RV_Button(RecycleDataViewBehavior, ButtonBehavior, StackLayout):
    index = None  # stores our index
    text = StringProperty('')
    def __init__(self, **kwargs):
        super(RV_Button, self).__init__(**kwargs)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(RV_Button, self).refresh_view_attrs(rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        pass

    def selectrv(self,*arg):
        pass

class RV_Label(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(RV_Label, self).__init__( **kwargs)
        self.markup = True
        self.text_size = self.size
        self.bind(size= self.on_size)
        self.bind(text= self.on_text_changed)
        self.size_hint_y = None # Not needed here

    def on_size(self, widget, size):
        self.text_size = size[0], None
        self.texture_update()
        if self.size_hint_y == None and self.size_hint_x != None:
            self.height = max(self.texture_size[1], self.line_height)
        elif self.size_hint_x == None and self.size_hint_y != None:
            self.width  = self.texture_size[0]

    def on_text_changed(self, widget, text):
        self.on_size(self, self.size)
