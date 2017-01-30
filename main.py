from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ListProperty, OptionProperty, ObjectProperty, StringProperty, DictProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.selectableview import SelectableView
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.checkbox import CheckBox
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



class EditButton(ToggleButtonBehavior, SelectableView, BoxLayout):

    def ans_state(self, checkbox, values, ansid):
        if values:
            newid = {ansid, True}
        else:
            newid = {ansid, False}






class StageButton(ListItemButton):
    pass



class GsamApp(App):
    projects = ListProperty([])
    stages = ListProperty([])
    questions = DictProperty({})
    answers = DictProperty({})



    def on_error(self, request, result):
        s = request.resp_status
        # print('failure: {0}'.format(s))


    def project_questions(self, req, results):
        for q in results['questions']:


            self.questions.update(q)
            print q



    def stage_list(self, req, results):

        print('project_sucess')
        for d in results['stages']:
            self.stages.options = d['name']

    def localprojects(self, req, results):
        print('success')
        # print(results)
        for d in results['projects']:

            pr = d['prj']['name']
            # pn = d['loc']['ending']
            # st = d['stages'][0]['name']

            self.projects.append(pr)
            # self.projects.append(pn)
            # self.projects.append(st)
            # print self.projects


    def build(self):
        UrlRequest('http://136.243.58.29:9191/projects/api/locals', self.localprojects, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)

        UrlRequest('http://136.243.58.29:9191/projects/api/stages', self.stage_list, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)

        UrlRequest('http://136.243.58.29:9191/projects/api/questions', self.project_questions, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)


        return

app = GsamApp()
app.run()