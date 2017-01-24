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
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.app import App

from kivy.properties import ListProperty, DictProperty, ObjectProperty, StringProperty, BooleanProperty

from modules.countrycodes import COUNTRY_CODES
from roomlist import CountryButton

from kivy.metrics import dp

import re
import logging
from itertools import chain
from operator import itemgetter
from functools import partial
import json
from kivy.uix.behaviors.button import ButtonBehavior

class SelectedCountryLabel(Label):
    def __init__(self, **kwargs):
        super(SelectedCountryLabel, self).__init__(**kwargs)

class PasswordToggleSelector(BoxLayout):
    # 'yes' 'no' or 'both
    password = StringProperty()
    yes_btn = ObjectProperty()
    no_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super(PasswordToggleSelector, self).__init__(**kwargs)

    def toggle_password(self):
        yes = self.yes_btn
        no = self.no_btn
        if yes.state == 'normal' and no.state == 'normal':
            self.password = 'both'
        elif yes.state == 'down':
            self.password = 'yes'
        else:
            self.password = 'no'

    def init_buttons(self):
        yes = self.yes_btn
        no = self.no_btn
        if self.password == 'both':
            yes.state = 'normal'
            no.state = 'normal'
        elif self.password == 'yes':
            yes.state = 'down'
            no.state = 'normal'
        else:
            yes.state = 'normal'
            no.state = 'down'


class CountrySelectionButton(ButtonBehavior, BoxLayout):

    country_code = StringProperty('xx')
    text = StringProperty('')
    selected = BooleanProperty(True)
    switch = ObjectProperty()

    def __init__(self, **kwargs):

        self.orientation = 'horizontal'

        super(CountrySelectionButton, self).__init__(**kwargs)

class CountrySelectionPopup(Popup):

    selected_countries = DictProperty({})
    deselected_countries = DictProperty({})
    layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(CountrySelectionPopup, self).__init__(**kwargs)
        self.add_country_buttons(self.layout)
        self.bind(on_dismiss=self.apply_changes)

    def add_country_buttons(self, layout):

        countries = sorted(COUNTRY_CODES.items(), key=itemgetter(1))

        for country in countries:

            btn = CountrySelectionButton(
                    text=country[1],
                    country_code=country[0])

            if btn.selected:
                self.selected_countries[country[0]] = btn
            else:
                self.deselected_countries[country[0]] = btn

            layout.add_widget(btn)

    def select_country(self, country_code):
        cc = country_code
        if cc not in self.selected_countries:
            btn = self.deselected_countries[cc]
            btn.selected = True
            self.selected_countries[cc] = btn
            del self.deselected_countries[cc]

    def deselect_country(self, country_code):
        cc = country_code
        if cc not in self.deselected_countries:
            btn = self.selected_countries[cc]
            btn.selected = False
            self.deselected_countries[cc] = btn
            del self.selected_countries[cc]

    def select_all(self):
        for child in self.layout.children:
            child.selected = True

    def deselect_all(self):
        for child in self.layout.children:
            child.selected = False

    def apply_changes(self, instance):

        new_selected = {}
        new_deselected = {}

        for child in self.layout.children:

            cc = child.country_code
            if child.selected:
                new_selected[cc] = child
            if not child.selected:
                new_deselected[cc] = child

        self.selected_countries = new_selected
        self.deselected_countries = new_deselected

class RoomFilterPanel(BoxLayout):

    country_selection_popup = ObjectProperty()
    name_input = ObjectProperty()
    password_selection = ObjectProperty()
    blocked_countries = ObjectProperty()

    blocked_country_btn_map = DictProperty({})

    def __init__(self, **kwargs):

        self.register_event_type('on_filters_changed')

        self.bind(name_input=self._init_name_input)
        self.bind(password_selection=self._init_password_selection)
        self.bind(blocked_countries=self._init_blocked_countries)

        self.country_selection_popup = CountrySelectionPopup()
        self._init_country_selection_popup(self, self.country_selection_popup)
        super(RoomFilterPanel, self).__init__(**kwargs)

    def _init_name_input(self, rfp, name_input):
        app = App.get_running_app()
        name = app.config.get('Filters', 'Name')
        name_input.text = name

        name_input.bind(text=partial(self.dispatch, 'on_filters_changed'))

    def _init_password_selection(self, rfp, password_selection):
        app = App.get_running_app()
        password = app.config.get('Filters', 'Password')
        password_selection.password = password
        password_selection.init_buttons()

        password_selection.bind(
                password=partial(self.dispatch, 'on_filters_changed'))

    def _init_country_selection_popup(self, rfp, obj):

        # read the config in before assigning observers
        blocked_countries_config = self.get_country_config()

        for country_code in blocked_countries_config:
            self.deselect_country(country_code)

        obj.bind(deselected_countries=partial(self.dispatch, 'on_filters_changed'))
        obj.bind(deselected_countries=self._refresh_blocked_countries_layout)

    def _init_blocked_countries(self, rfp, blocked_countries):
        self._refresh_blocked_countries_layout(self,
                self.country_selection_popup.deselected_countries)

    def on_filters_changed(self, *args):
        pass

    def _refresh_blocked_countries_layout(self, rfp, deselected_countries):

        self.blocked_countries.clear_widgets()

        for country_code, btn in deselected_countries.items():

            country = COUNTRY_CODES[country_code]
            indicator_btn = CountryButton(text=country,
                    country_code=country_code,
                    size_hint_y=None, height=dp(24))

            indicator_btn.bind(on_press=partial(self.select_country,country_code))
            self.blocked_countries.add_widget(indicator_btn)

    def select_country(self, *args):
        self.country_selection_popup.select_country(args[0])

    def deselect_country(self, *args):
        self.country_selection_popup.deselect_country(args[0])

    def create_country_config(self):
        """
        Creates a string of deselected country codes that can be saved to apps
        config.
        """
        countries_config = []

        countries = self.country_selection_popup.deselected_countries
        return ' '.join(country_code
                for country_code, btn in countries.items())

    def get_country_config(self):
        app = App.get_running_app()
        blocked_countries_config = app.config.get('Filters', 'Countries')

        return blocked_countries_config.split()

    def room_passed(self, room):
        """
        Returns True if room passes the filters (meaning any of the filter DO
        NOT apply for this room and False if does not pass.
        """

        passed = True

        string = self.name_input.text
        if not re.search(string.lower(), room['name'].lower()):
            passed = False

        password = self.password_selection.password
        if not (password == 'both'):
            password = True if password == 'yes' else False
            if room['password'] is not password:
                passed = False

        deselected_countries = self.country_selection_popup.deselected_countries
        for country_code, btn in deselected_countries.items():
            if (room['country_code'] == country_code):
                passed = False
                break

        return passed

    def filter_roomlist(self, roomlist, filtered):
        """
        Updates roomlist and filtered lists. Does not modify given lists, but
        returns new ones.
        """

        logging.info('Filtering roomlist started')

        new_filtered = []
        new_rooms = []

        for room in chain(roomlist,filtered):
            if self.room_passed(room):
                new_rooms.append(room)
            else:
                new_filtered.append(room)

        return (new_rooms, new_filtered)
