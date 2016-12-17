from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import OptionProperty
from kivy.storage.jsonstore import JsonStore

from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, ObjectProperty






import json
from kivy.lang import Builder


localpr = JsonStore('localpr.json')



class MyScreenManager(ScreenManager):
    pass


class IntroScreen(Screen):
    pass

class FormScreen(Screen):
    pass

class MediaScreen(Screen):
    pass

class ProjectScreen(Screen):
    pass


class ProjectEditScreen(Screen):
    pass

class ListingScreen(Screen):
    pass

class ProjectActivityScreen(Screen):
    pass



class ActivityScreen(Screen):
    pass


class MessageScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass




class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,RecycleBoxLayout):
    pass

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





class GsamApp(App):
    projects = ListProperty([])
    stages = OptionProperty(None, options=[])

    def on_error(self, request, result):
        s = request.resp_status
        # print('failure: {0}'.format(s))

    # def stage_list(self, req, results):
    #
    #     print('project_sucess')
    #     for d in results['stages']:
    #         self.stages.options = d['name']

    def localprojects(self, req, results):
        print('success')
        # print(results)
        for d in results['projects']:

            # print  [f['name'] for f in d['stages']]

            pr = d['prj']['name']
            # pn = d['loc']['ending']
            # st = d['stages'][0]['name']

            self.projects.append(pr)
            # self.projects.append(pn)
            # self.projects.append(st)


    def build(self):
        UrlRequest('http://136.243.58.29:9191/projects/api/locals', self.localprojects, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)

        # UrlRequest('http://136.243.58.29:9191/projects/api/locals', self.stage_list, on_failure=self.on_error,
        #            on_error=self.on_error, decode=True, timeout=10)

        return


GsamApp().run()