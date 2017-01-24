from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ListProperty, OptionProperty, ObjectProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import json
from kivy.lang import Builder



localpr = JsonStore('localpr.json')



class MenuPopup(Popup):
    def on_press_dismiss(self, *args):
        self.dismiss()
        return False

class PaintWindow(BoxLayout):
    pass

class MyScreenManager(ScreenManager):
    pass


class IntroScreen(Screen):
    pass


class ProjectScreen(Screen):
    pass








class ProjectEditScreen(Screen):
    yes = ObjectProperty(True)
    no = ObjectProperty(False)

class ProjectActivityScreen(Screen):
    projname = StringProperty()
    project_acts = ObjectProperty()
    pass



class ActivityScreen(Screen):
    pass


class MessageScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass

class MenuButton(ListItemButton):
    def open_popmenu(self, text):
        popmenu = MenuPopup()
        popmenu.title = text
        popmenu.open()
        # upd_screen = ProjectActivityScreen()
        # upd_screen.projname = text
        app.root.ids.project_acts.projname = text


class StageButton(ListItemButton):
    pass



class GsamApp(App):
    projects = ListProperty([])
    stages = ListProperty([])


    def on_error(self, request, result):
        s = request.resp_status
        # print('failure: {0}'.format(s))

    def stage_list(self, req, results):

        print('project_sucess')
        for d in results['stages']:
            self.stages.options = d['name']

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
        UrlRequest('http://136.243.58.29:9090/projects/api/locals', self.localprojects, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)

        UrlRequest('http://136.243.58.29:9090/projects/api/stages', self.stage_list, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)


        return

app = GsamApp()
app.run()