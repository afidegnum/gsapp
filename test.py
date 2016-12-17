from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

Builder.load_string('''

MyScreenManager:
    ProjectEditScreen:

<SelectableLabel>:
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        BoxLayout:
            padding: 50, 50
            size_hint_x: .8
            size_hint_y: .3
            Button:
                id: 'updateproject'
                on_release: app.root.current = 'basicform'
                background_color: 0,0,0,0
                Image:
                    source: 'home.png'
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                    size: 30, 30
            Label:
                text: root.text
            Button:
                id: 'loadmedia'
                on_release: self.load_media
                background_color: 0,0,0,0
                Image:
                    source: 'projects.png'
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                    size: 30, 30
Screen:
    name: 'basicform'
    GridLayout:
        cols:1
        TextInput:
            id: _a
            text: '3'
        TextInput:
            id: _b
            text: '5'
        Label:
            id: _result
        Button:
            text: 'sum'
            # You can do the opertion directly
            on_press: _result.text = str(int(_a.text) + int(_b.text))
        Button:
            text: 'product'
            # Or you can call a method from the root class (instance of calc)
            on_press: root.product(*args)
Screen:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)

<RV>:
    viewclass: 'SelectableLabel'
    SelectableRecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
        touch_multiselect: False
        update_form: 'updateproject'

''')


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

from kivy.properties import StringProperty
class SelectableLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    text = StringProperty()



    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]

    def update_project(self, index, data):
        #laod form
        print "index:"+index+"   "+"data:"+data

    def load_media(self, index, data):
        #laod form
        print "index:"+index+"   "+"data:"+data


class TestApp(App):
    def build(self):
        return RV()

if __name__ == '__main__':
    TestApp().run()