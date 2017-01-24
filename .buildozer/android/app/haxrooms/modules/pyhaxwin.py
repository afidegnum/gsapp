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

from subprocess import Popen, PIPE
import logging
import os
import time

class Communicator(object):
    """Class for handling communication to HaxWin through anonymous pipe."""

    #HAXWIN_DIR = '..\\..\\..\\HaxWin\\HaxWin\\bin\\Release'
    HAXWIN_DIR = 'HaxWin'
    HAXWIN_PATH = os.path.join(HAXWIN_DIR, 'HaxWin.exe')

    # codes for communication
    NAVIGATE = "NAV"

    def __init__(self):
        super(Communicator, self).__init__()
        self.haxwin = None
        
    def _run_haxwin(self):
       self.haxwin = Popen([self.HAXWIN_PATH, '--com'], cwd=self.HAXWIN_DIR,
			        shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def _write(self, data):
        if not self.is_haxwin_alive():
            self._run_haxwin()
        
        logging.debug("Writing to pipe: {0}".format(data))
        self.haxwin.stdin.write(data)
        self.haxwin.stdin.flush()

    def is_haxwin_alive(self):

        if self.haxwin is not None:
            returncode = self.haxwin.poll()
            
            if returncode is not None:
                return False
            else:
                return True
        else:
            return False
        
    def send_msg(self, code, data):
        # construct the message to form [CODE][SPACE][DATA][NULLBYTE]
        msg_str = code + " " + data + '\x00';
        # convert message to bytes
        byte_str = msg_str.encode(encoding='UTF-8')
        return self._write(byte_str)

        
    def navigate(self, url):
        return self.send_msg(self.NAVIGATE, url)

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    com = Communicator()
    """
    f = open("testinput.txt", "wb")
    test_string = 'NAV http://www.haxball.com/?room_id=~B12341234' + '\x00'
    f.write(test_string.encode(encoding='UTF-8'))
    f.close()
    """
    com.navigate('http://www.haxball.com/?room_id=~B12341234')
    time.sleep(4)
    com.navigate('http://www.haxball.com/?room_id=~B1242142341234')

    print(com.haxwin.stdout.read(-1).decode(encoding='UTF-8'))
