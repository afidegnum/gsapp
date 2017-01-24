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
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.core.window import Window

class HoverBehavior(object):
    """Hover behavior. :Events: `on_enter` Fired when mouse enter the bbox of
    the widget. `on_leave` Fired when the mouse exit the widget """

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can be
    used in `on_enter` or `on_leave` in order to know where was dispatched the
    event. '''
    def __init__(self, **kwargs):

        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed
        # Next line to_widget allow to compensate for relative layout
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))

        if self.hovered == inside: #We have already done what was needed
            return

        self.border_point = pos
        self.hovered = inside

        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass
    def on_leave(self):
        pass

