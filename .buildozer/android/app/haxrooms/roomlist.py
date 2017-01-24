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
from modules.haxroomlist import HaxRoomListParser
from modules.countrycodes import COUNTRY_CODES

from behaviors import HoverBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView

from kivy.properties import StringProperty, BooleanProperty, ListProperty, ObjectProperty

from kivy.network.urlrequest import UrlRequest

import threading
import logging

class RoomListRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(RoomListRecycleView, self).__init__(**kwargs)
        
class RoomListRow(BoxLayout):

    name = StringProperty('')
    players = ListProperty('')
    players_string = StringProperty('')
    password = BooleanProperty()
    country = StringProperty('')
    country_code = StringProperty('')
    url = StringProperty('')
    distance = StringProperty('')

    def __init__(self, **kwargs):
        super(RoomListRow, self).__init__(**kwargs)

class ActButton(ButtonBehavior, HoverBehavior, Image):
    pass

class SortButton(ButtonBehavior, HoverBehavior, Label):
    pass

class CountryButton(ButtonBehavior, HoverBehavior, BoxLayout):

    select_on_press = BooleanProperty(False)
    country_code = StringProperty('')
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(CountryButton, self).__init__(**kwargs)

    def on_leave(self):
        for child in self.children:
            child.color = [1,1,1,.7]
    def on_enter(self):
        for child in self.children:
            child.color = [1,1,1,1]

class RoomList(BoxLayout):

    list_url = "http://www.haxball.com/list3"
    _cache_version = 0

    rooms = ListProperty([])
    filtered = ListProperty([])

    filter_panel = ObjectProperty()

    room_parse_event = None

    sort_key = StringProperty('name')
    reverse_sort = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.bind(filter_panel=self.set_filter_observer)

        super(RoomList, self).__init__(**kwargs)


    def set_filter_observer(self, roomlist, filter_panel):
        filter_panel.bind(on_filters_changed=self._apply_filters)

    def sort_roomlist(self, key, roomlist=None):

        logging.info('Sorting roomlist.')
        # if roomlist was given as argument we sort that and return it instead
        # of modifying the object property and without toggling the reverse
        if roomlist is not None:
            return self._sort_roomlist(roomlist)

        # toggle reverse sorting if sort key is same
        if key == self.sort_key:
            self.reverse_sort = not self.reverse_sort
        else:
            self.sort_key = key

        # if no roomlist as arg we modify the object property
        self.rooms = self._sort_roomlist(self.rooms)

    def _sort_roomlist(self, roomlist):

        key = self.sort_key

        logging.debug('key: ' + key)

        if not key:
            key = 'name'

        if key is 'players':
            roomlist = sorted(roomlist, key=lambda k: k [key][0],
                    reverse=self.reverse_sort)
        else:
            roomlist = sorted(roomlist, key=lambda k: k [key],
                    reverse=self.reverse_sort)

        return roomlist

    def fetch_roomlist(self, *args, **kwargs):

        logging.info('Fetching roomlist.')

        if 'on_success' not in kwargs:
            on_success = self._list_downloaded
        else:
            on_success = kwargs['on_success']
        if 'on_failure' not in kwargs:
            on_failure = self._list_download_failed
        else:
            on_failure = kwargs['on_failure']

        UrlRequest(self.list_url, on_success=on_success, on_failure=on_failure)

    def _list_downloaded(self, request, result):

        logging.info('Roomlist downloaded.')

        parser = HaxRoomListParser(result)
        cache_version = parser.get_cache_version()

        logging.debug('cache_version: ' + str(cache_version))

        if self._cache_version != cache_version:
            self._cache_version = cache_version

            self.parser_thread = threading.Thread(target=self._parse_rooms,
                    args=(parser,))

            self.parser_thread.start()


    def _list_download_failed(self, request, result):
        pass

    def _parse_rooms(self, parser):

        logging.info('Roomlist parsing started.')

        new_filtered = []
        new_rooms = []

        for room in parser:

            room_dict = ({
                'name': room.name,
                'players_string': room.players_string,
                'players': room.players,
                'password': room.password,
                'country': room.country,
                'country_code': room.country_code,
                'url': room.url,
            })


            if self.filter_panel.room_passed(room_dict):
                new_rooms.append(room_dict)
            else:
                new_filtered.append(room_dict)

        self.filtered = new_filtered
        self.rooms = self.sort_roomlist(key=self.sort_key, roomlist=new_rooms)

    def _apply_filters(self, *args):
        """
        This is called when filters change.
        """
        logging.info('Roomlist filter applying started.')

        (self.rooms, self.filtered) = self.filter_panel.filter_roomlist(
                                        self.rooms, self.filtered)

