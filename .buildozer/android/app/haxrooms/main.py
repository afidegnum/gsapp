# -*- coding: utf-8 -*-
"""
HaxRooms - room browser for flash based game haxball
Copyright (C) 2016  Oskari Pöntinen <mail.morko@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from roomlist import RoomList, CountryButton
from roomlistfilter import CountrySelectionPopup
from behaviors import HoverBehavior
from modules.pyhaxwin import Communicator

from kivy.app import App
from kivy.uix.label import Label

from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, StringProperty

from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.core.window import Window

import threading
from functools import partial
import sys
import logging
import webbrowser
import os

class SettingsButton(ButtonBehavior, HoverBehavior, Image):
    def __init__(self, **kwargs):
        super(SettingsButton, self).__init__(**kwargs)

class RefreshButton(ToggleButtonBehavior, HoverBehavior, Image):
    angle = NumericProperty(360)

    def __init__(self, **kwargs):
        super(RefreshButton, self).__init__(**kwargs)

    def rotate(self, btn):
        if self.angle == 0:
            self.angle = 320
        else:
            self.angle -= 40

    def start_rotation(self):
        Clock.schedule_interval(self.rotate, .08)

    def stop_rotation(self):
        Clock.unschedule(self.rotate)

class AlertPopup(Popup):
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(AlertPopup, self).__init__(**kwargs)
        self.title = 'Alert'
        self.size_hint = (None, None)
        self.size = (dp(600), dp(400))
        
        self.layout = BoxLayout(orientation='vertical')
        
        self.label = Label(text=self.text, valign='middle', halign='center')
        self.label.bind(size=self.label.setter('text_size'))
        self.bind(text=self.label.setter('text'))
        
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)

    def error(self, msg):
        self.label.text = msg
        close_btn = Button(text='Close', size_hint_y=None, height=dp(30))
        close_btn.bind(on_press=partial(self.dismiss))
        self.layout_add_widget(close_btn)
        self.open()

    def action(self, msg, btn_text, callback):
        self.label.text = msg
        action_btn = Button(text=btn_text, size_hint_y=None, height=dp(30))
        action_btn.bind(on_press=partial(self.dismiss))
        action_btn.bind(on_press=callback)
       
        self.layout.add_widget(action_btn)
        self.open()
        
    def on_dismiss(self):
        for child in self.layout.children:
            if child is not self.label:
                self.layout.remove_widget(child)

        
class HaxRoomsRoot(GridLayout):
    """
    Applications Root Widget
    """

    refreshing_enabled = False

    app = ObjectProperty()
    roomlist = ObjectProperty()
    filter_panel = ObjectProperty()
    alert_popup = ObjectProperty()
    refresh_callback = None
    selected_country_btn_map = {}

    # controller/communicator for HaxWin browser
    haxwincom = Communicator()
    
    def __init__(self, **kwargs):
        self.bind(roomlist=self._init_roomlist)
        self.alert_popup = AlertPopup()

        super(HaxRoomsRoot, self).__init__(**kwargs)

    def _init_roomlist(self, root, roomlist):
        self.refresh_callback = roomlist.fetch_roomlist
        self.refresh_callback()

    def refresh_roomlist_pressed(self, btn, state):

        cb = self.refresh_callback

        if state == 'down':
            self.refreshing_enabled = True
            # refresh once immediately
            cb()
            Clock.schedule_interval(cb, 12)
            btn.rotate(btn)
            btn.start_rotation()
        else:
            self.refreshing_enabled = False
            Clock.unschedule(cb)
            btn.stop_rotation()

    def copy_room_pressed(self, url):
        Clipboard.copy(url)
        
    def join_room_pressed(self, url):

        browser = self.app.config.get('General', 'Browser')

        if browser != 'HaxWin Browser':

            try:
                browser = webbrowser.get(browser)
            except:
                self.alert_popup.error("Could not open browser:\n" + browser +
                                       "Try changing browser from the settings.")
                return
            browser.open(url, new=2)
        else:
            self.haxwincom.navigate(url)


    def sort_roomlist_pressed(self, key):
        self.roomlist.sort_roomlist(key=key)

    def roomlist_country_button_pressed(self, country_code):
        self.filter_panel.deselect_country(country_code)

    def settings_button_pressed(self):
        self.app.open_settings()

class HaxRooms(App):
    """
    Main Application Class
    """
    icon = "icon.png"
    browsers = []

    def __init__(self, **kwargs):
        self.detect_browsers()
        super(HaxRooms, self).__init__(**kwargs)

    def build(self):
        
        LabelBase.register(name="NotoSerif",
                   fn_regular="fonts/NotoSerif-hinted/NotoSerif-Regular.ttf",
                   fn_bold="fonts/NotoSerif-hinted/NotoSerif-Bold.ttf",
                   fn_italic="fonts/NotoSerif-hinted/NotoSerif-Italic.ttf",
                   fn_bolditalic="fonts/NotoSerif-hinted/NotoSerif-BoldItalic.ttf")

        # create the root widget and give it a reference of the application
        # instance (so it can access the application settings)
        root = HaxRoomsRoot()
        root.app = self
        return root

    def detect_browsers(self):

        # detect browsers from windows registry
        if sys.platform[:3] == "win":
            import winreg
            ikey = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'software\clients\startmenuinternet')
            bkeys = []
            try:
                i = 0
                while True:
                    bkeys.append(winreg.EnumKey(ikey, i))
                    i += 1
            except EnvironmentError:
                pass

            for br in bkeys:
                bkey = winreg.OpenKey(ikey, br)

                # get the default value from shell\open\command
                br_cmd = winreg.QueryValue(bkey, r'shell\open\command')
                if br_cmd.startswith('"') and br_cmd.endswith('"'):
                    br_cmd = br_cmd[1:-1]

                # get ApplicationName from Capabilities
                try:
                    bcapkey = winreg.OpenKey(bkey, r'capabilities')
                    br_name = winreg.QueryValueEx(bcapkey, r'ApplicationName')[0]
                except FileNotFoundError:
                    br_name = br_cmd.split('\\')[-1]

                self.browsers.append(br_name)
                # register browser name and executable path for webbrowser
                webbrowser.register(
                    br_name, None, webbrowser.BackgroundBrowser(br_cmd))

            # add the default HaxWin Browser
            self.browsers.append('HaxWin Browser')

    def build_settings(self, settings):

        browsers = str(self.browsers)
        browsers = browsers.replace("'", '"')
        
        setting_panel_data = """
        [
            { "type": "title",
              "title": "Configurations" },

            { "type": "options",
              "title": "Browser",
              "desc": "Browser to open when joining rooms.",
              "section": "General",
              "key": "Browser",
              "options": """ + browsers + """ }
        ]
        """

        settings.add_json_panel('HaxRooms settings', self.config,
                data=setting_panel_data)


    def build_config(self, config):

        config.setdefaults('General', {
                'Browser': 'HaxWin Browser'
        })

        config.setdefaults('Filters', {
                'Name': '',
                'Password': 'both',
                'Countries': ''
        })

    def on_stop(self):
        name = self.root.filter_panel.name_input.text
        password = self.root.filter_panel.password_selection.password
        countries = self.root.filter_panel.create_country_config()
        self.config.set('Filters', 'Name', name)
        self.config.set('Filters', 'Password', password)
        self.config.set('Filters', 'Countries', countries)
        self.config.write()

if __name__ == '__main__':
    logger = logging.getLogger("mylogger")
    
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    
    logger.addHandler(handler)

    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
    HaxRooms().run()
