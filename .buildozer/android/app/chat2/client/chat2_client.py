from kivy.support import install_twisted_reactor
from twisted.protocols.basic import LineReceiver
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.uix.stacklayout import StackLayout
from kivy.clock import Clock, mainthread
from kivy.uix.label import Label
from kivy.app import App
install_twisted_reactor()
from twisted.internet import reactor, protocol
from time import time, sleep, strftime
import os
default_username = 'User'
default_colors = {
    'time_col': '#BDBDBD',
    'text_col': '#F2F2F2',
    'err_col': '#FF4E4E',
    'chan_col': '#0B6121'
}

def get_time_sec():
    return strftime('%H:%M:%S')

def focus_widget(widget):
    widget.focus = True

def add_word_color(text, textfind, color, targets=[0]):
    text = text.split(' ')
    for i, word in enumerate(text):
        if textfind in word:
            for x in targets:
                text[i+x] = '[color=%s]%s[/color]' % (color, text[i+x])
    return ' '.join(text)

class EchoClient(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.tryname = 1

    def connectionMade(self):
        self.factory.app.on_connection(self)
        self.sendLine("NICK %s" % (default_username))
        self.sendLine("JOIN #AA")

    def lineReceived(self, data):
        if data[:8] == 'NICK ERR':
            self.tryname += 1
            self.sendLine("NICK %s%s" % (default_username, self.tryname))
        self.factory.app.print_message(data)

    def connectionLost(self, reason):
        self.factory.app.print_message("connection lost")


class EchoFactory(protocol.ClientFactory):
    protocol = LineReceiver
    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        self.app.print_message("Connection lost")

    def clientConnectionFailed(self, conn, reason):
        self.app.print_message("Connection failed")

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        return EchoClient(self)

    def clientConnectionFailed(self, connector, reason):
        self.app.print_message("Connection failed.")

    def clientConnectionLost(self, connector, reason):
        self.app.print_message("Connection lost.")



class Chat2Client(StackLayout):
    connection = None
    action_bar_line_height = NumericProperty(100)
    def __init__(self, **kwargs):
        super(Chat2Client, self).__init__(**kwargs)
        self.username = ''
        self.rvd = self.ids.rv.data
        self.textbox = self.ids.textbox
        self.col = default_colors
        self.ids.rv.scroll_y = 0.0
        self.connect_to_server('localhost', 44672)

    def rvd_add(self, text):
        scroller_y = self.ids.rv.scroll_y = 0.0
        text = add_word_color(text, 'ERR', self.col['err_col'], targets=[0,1])
        text = add_word_color(text, '#', self.col['chan_col'], targets=[0])
        tm = '[color=%s]%s[/color]' % (self.col['time_col'], get_time_sec())
        text1 = '[color=%s]%s[/color]' % (self.col['text_col'], text)
        text2 = '%s %s' % (tm, text1)
        # print text
        # print text2
        self.ids.rv.data.append({'text': text2})
        self.ids.rv.refresh_from_data()
        if scroller_y == 0.0 or scroller_y == -0.0:
            self.ids.rv.scroll_y = -0.0

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        self.textbox.bind(on_text_validate=self.send_message)
        self.label = Label(text='connecting...\n')
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.textbox)
        return self.layout

    def connect_to_server(self, ip, port):
        reactor.connectTCP(ip, port, EchoFactory(self))
        self.rvd_add('Connecting to %s:%s' % (ip, port))

    def on_connection(self, connection):
        self.rvd_add('Connected successfuly')
        self.connection = connection
        tx1, tx2 = str(connection.transport.getPeer()), []
        tx1 = tx1.split('(')
        tx1 = tx1[1].split(',')
        for x in tx1: tx2.append(x)
        for i, text in enumerate(tx2):
            text = list(text)
            deleted = 0
            for ic, char in enumerate(tx2[i]):
                if char in (' ', '"', ')') or char == "'":
                    ic2 = ic - deleted
                    del text[ic2]
                    deleted += 1
            tx2[i] = ''.join(text)
        self.ids.actionbar_label.text = '[size=22]Chat %s@%s/%s[/size]' % (tx2[0], tx2[1], tx2[2])


    def on_disconnect(self, *args):
        self.ids.actionbar_label.text = ''

    def send_message(self, *args):
        msg = self.textbox.text
        if msg and self.connection:
            self.connection.sendLine(str(self.textbox.text))
            self.rvd_add('Sending %s' % (str(self.textbox.text)))
            self.textbox.text = ""
        elif not self.connection:
            self.rvd_add('Not connected')
        Clock.schedule_once(lambda x: focus_widget(self.textbox), 0)

    def print_message(self, msg):
        if msg[:8] == 'NICK ERR' and not self.username:
            self.ids.username.text = '[color=%s][b]ERR[/b][/color]' % (self.col['err_col'])
        if msg[:8] == 'NICK SET':
            self.ids.username.text = msg[8:]
        self.rvd_add(msg)


class Chat2ClientApp(App):

    def build(self):
        self.chatgui = Chat2Client()
        return self.chatgui

if __name__ == '__main__':
    Chat2ClientApp().run()
