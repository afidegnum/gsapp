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

"""
From http://pastebin.com/7H1MACJm

basro_	anyway, the room list is a compressed binary file
basro_	which you can obtain @ www.haxball.com/list3
basro_	it is compressed with zlib deflate
basro_	after decompression the format is as follows: (wait a bit must open the source file)
basro_	1 byte ; list format version ( currently = 1 )
basro_	4 bytes ; skip this, you don't care about them
basro_	then follows a list of RoomInfo structures until the end of the file
basro_	this is the room info structure:
basro_	data.writeShort(ver);
basro_	data.writeUTF(netID);
basro_	data.writeUTF(name);
basro_	data.writeByte(players);
basro_	data.writeByte(maxPlayers);
basro_	data.writeBoolean(password);
basro_	data.writeUTF(countryCode);
basro_	data.writeFloat(latitude);
basro_	data.writeFloat(longitude);
basro_	that's all
"""

import logging
import struct
import zlib
import time
import urllib.request
import sys
#from modules.countrycodes import COUNTRY_CODES
from countrycodes import COUNTRY_CODES

class HaxRoom(object):

    URL_PREFIX = 'http://www.haxball.com/?roomid='

    def __init__(self, version, net_id, name, players, password,
            country_code,cordinates):

        self.version = version
        self._net_id = net_id
        self.name = name
        self._players = players
        self.password = password
        self._country_code = country_code
        self.cordinates = cordinates

        self.url = self.make_url()
        self.players_string = self.make_players_string()
        self.country = self.make_country()

    def make_country(self):

        if self._country_code not in COUNTRY_CODES:
            self._country_code = 'xx'

        return COUNTRY_CODES[self.country_code]

    def make_url(self):
        return self.URL_PREFIX + self._net_id

    def make_players_string(self):
        return str(self._players[0]) + '/' + str(self._players[1])

    @property
    def net_id(self):
        return self._net_id

    @net_id.setter
    def net_id(self, value):
        self._net_id = value
        self.url = self.make_url()

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, value):
        self._players = value
        self.players_string = self.make_players_string()

    @property
    def country_code(self):
        return self._country_code

    @country_code.setter
    def country_code(self, value):
        self._country_code = value
        self.country = self.make_country()

    @country_code.getter
    def country_code(self):
        return self._country_code

    def to_string(self):
        string = (self.name + ' || ' + self.url + ' || ' +
                  str(self.players) + ' || ' + self.country)
        if sys.platform[:3] == "win":
            winbytestring = string.encode('cp1252', 'ignore')
            string = winbytestring.decode('cp1252')
        return string
class HaxRoomListFetcher:

    url = "http://www.haxball.com/list3"

    @classmethod
    def fetch(self):

        req = urllib.request.Request(self.url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64)')
        response = urllib.request.urlopen(req)
        bytelist = response.read()
        return bytelist

class HaxRoomListParser:

    def __init__(self, byteroomlist):
        # set offset of 5 because of list header
        self.index = 5
        self.byte_counter = 0
        self.byteroomlist = self.decompress(byteroomlist)
        self.size = len(self.byteroomlist)
        logging.debug('Created new HaxRoomListParser. Size of byteroomlist is ' +
                str(self.size) + '.')

    def decompress(self, byteroomlist):
        return zlib.decompress(byteroomlist)

    def get_cache_version(self):
        cache_version = struct.unpack('!I', self.byteroomlist[1:5])[0]
        logging.debug('HaxRoomList cache version is ' + str(cache_version) + '.')
        return cache_version

    def readBytes(self, size):
        """
        Reads the given size length of bytes from the current position in
        byteroomlist and increases the self.byte_counter accordingly.
        Current position is self.index + self.byte_counter.
        """

        bytes = self.byteroomlist[
                self.index + self.byte_counter : self.index + self.byte_counter+size]

        self.byte_counter += size

        return bytes

    def __iter__(self):
        return self

    def __next__(self):

        if self.size <= self.index:
            raise StopIteration()

        room = {}

        # first 2 bytes are lenght of the whole room information bytes
        room_length_bytes = struct.unpack('!H', self.readBytes(2))[0]

        # room version is 2 byte long unsigned short
        room['version'] = struct.unpack('!H', self.readBytes(2))[0]


        # next two bytes are the length of the net_id string. should be 66.
        net_id_length = struct.unpack('!H', self.readBytes(2))[0]

        # read the net_id
        room['net_id'] = self.readBytes(net_id_length).decode("utf-8", "strict")

        # next two bytes are the room name length
        name_length = struct.unpack('!H', self.readBytes(2))[0]

        # get the room name and decode with UTF-8
        room['name'] = self.readBytes(name_length).decode("utf-8", "replace")

        # next 3 bytes are players, max_players and password indicator
        room['players'] = struct.unpack('!BB', self.readBytes(2))
        room['password'] = struct.unpack('!?', self.readBytes(1))[0]

        # next 2 bytes are countrycodes length
        country_code_length = struct.unpack('!H', self.readBytes(2))[0]
        logging.debug('country_code_length: ' + str(country_code_length))

        # get country code and decode with UTF-8
        room['country_code'] = self.readBytes(country_code_length).decode(
                "utf-8", "replace")

        # next 8 bytes are the latitude and longitude of room in float
        room['cordinates'] = struct.unpack( '!ff', self.readBytes(8))
        
        roomobj = HaxRoom(**room)
        logging.debug('Parsed room: ' + roomobj.to_string())

        # add the total count of bytes read to the index counter of the roomlist
        self.index += self.byte_counter
        #reset byte_counter
        self.byte_counter = 0;

        return roomobj

class HaxRoomList:

    cache_version = 0
    refresh_time = 0
    URL_PREFIX = 'http://www.haxball.com/?roomid='

    def __init__(self, rooms=[]):
        self.rooms = rooms

    def __iter__(self):
        return self.rooms.__iter__()

    def append(self, room):
        self.rooms.append(room)

    def refresh(self):
        parser = HaxRoomListParser(HaxRoomListFetcher.fetch())
        cache_version = parser.get_cache_version()
        if self.cache_version != cache_version:
            self.cache_version = cache_version
            self.refresh_time = time.time()
            self.rooms = []
            for room in parser:
                self.append(room)
            return self.rooms

    def sort_by(self, key, reverse=False):
        return sorted(self.rooms, key=attrgetter(key), reverse=reverse)
