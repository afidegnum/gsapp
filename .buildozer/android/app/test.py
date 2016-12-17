

























from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.camera import Camera

import json
from kivy.lang import Builder


localpr = JsonStore('localpr.json')



class MyScreenManager(ScreenManager):
    pass


class IntroScreen(Screen):
    pass


class ProjectScreen(Screen):
    pass


class ProjectEditScreen(Screen):
    pass

class ProjectActivityScreen(Screen):
    pass



class ActivityScreen(Screen):
    pass


class MessageScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass


class GsamApp(App):
    projects = ListProperty([])

    def on_error(self, request, result):
        s = request.resp_status
        # print('failure: {0}'.format(s))

    def localprojects(self, req, results):
        print('success')
        # print(results)
        for d in results['projects']:

            # print  [f['name'] for f in d['stages']]

            pr = d['loc']['title']
            pn = d['loc']['ending']
            st = d['stages'][0]['name']

            self.projects.append(pr)
            self.projects.append(pn)
            self.projects.append(st)


    def build(self):
        UrlRequest('http://gsam.ga:9191/projects/api/localprj', self.localprojects, on_failure=self.on_error,
                   on_error=self.on_error, decode=True, timeout=10)
        return


GsamApp().run()