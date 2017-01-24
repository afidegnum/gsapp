# from socket import *
# from protocols import twisted_isptc
# from os import linesep as delimiter
from twisted.internet import protocol, reactor, endpoints, stdio
from twisted.internet.protocol import Factory
from twisted.internet import task
from twisted.protocols.basic import LineReceiver
from twisted.protocols.basic import NetstringReceiver
import threading
from time import sleep
import multiprocessing
from time import time, sleep
import random
import os
welcome_message = 'Welcome to chat2'
nick_minlen = 4
nick_maxlen = 20


def printer(*args,**kwargs):
    print args,kwargs


def tworker(parent, *arg):
    looping = True
    sleep(0.2)
    while parent.looping:
        a = raw_input('>> ')
        a = a.lower()
        if a == 'q':
            reactor.stop()
            sleep(0.1)
            parent.looping = False
            print '[Master] STOP'
            os._exit(0)
        elif a == 'c':
            print 'Channels:'
            for k, v in parent.channels.iteritems():
                print k, v
        elif a == 'u':
            print 'USERS:'
            for k, v in parent.users.iteritems():
                print k, v
        else:
            print '<<', a


class Master_Server(object):
    def __init__(self, users):
        self.users = {}
        self.channels = {}
        self.looping = True
        threading.Thread(target=tworker, args=([self])).start()
        print 'Started Master_Server'

    def user_add(self, nick, addr, obj):
        self.users[nick] = {'rname':'', 'chans':[], 'addr':addr, 'receiving':True, 'obj': obj,
                            'connected':True, 'hidden':False, 'ssid': str(random.getrandbits(512))}

    def user_set_nick(self, old, new):
        if new[0] in ('#', ' ', '!','?', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
            return (False, 'ERR FIRST_CHARACTER_ILLEGAL')
        elif new not in self.users:
            self.users[new] = self.users[old]
            del self.users[old]
            return (True, '')
        else:
            return (False, 'ERR NOT_AVAILABLE')

    def user_nick_from_ssid(self, nick, ssid):
        if self.users[nick]['ssid'] == ssid:
            return True
        else:
            return False

    def user_set_name(self, nick, name):
        self.users[nick] = name

    def user_set_addr(self, nick, addr):
        self.users[nick] = addr

    def user_enable_sender(self, nick):
        self.users[nick]['sender'][0] = True

    def user_disable_sender(self, nick):
        self.users[nick]['sender'][0] = False

    def user_set_connected(self, nick, boolean):
        self.users[nick]['connected'] = boolean

    def user_set_values(self, nick, dictio):
        self.users[nick].update(dictio)
        return True

    def user_join_channel(self, nick, channel):
        has_joined = True
        if channel[0] != '#':
            channel = '#'+channel
        try:
            if nick not in self.channels[channel]:
                has_joined = False
        except:
            self.channel_create(channel)
            if nick not in self.channels[channel]:
                has_joined = False
        if has_joined == False:
            for username in self.channels[channel]['users']:
                self.users[username]['obj'].joinMSG(channel, nick)
            self.channels[channel]['users'].append(nick)
            self.users[nick]['chans'].append(channel)
            return True
        else:
            return False

    def user_leave_channel(self, nick, channel):
        if channel[0] != '#':
            channel = '#'+channel
        if nick in self.channels[channel]['users']:
            self.channels[channel]['users'].remove(nick)
            self.users[nick]['chans'].remove(channel)
            for username in self.channels[channel]['users']:
                self.users[username]['obj'].leaveMSG(channel, nick)

    def user_quit(self, nick, reason=''):
        for chan in self.users[nick]['chans']:
            self.users[nick]['obj'].leaveMSG(chan, nick, reason)

    def user_get_channels(self, nick):
        return self.users[nick]['chans']

    def user_msg(self, source, target, message):
        if target[0] == '#':
            for nick in self.channels[target]['users']:
                if self.users[nick]['receiving']:
                    self.users[nick]['obj'].privMSG(source, target, message)
        else:
            if self.users[target]['receiving']:
                self.users[target]['obj'].privMSG(source, target, message)

    def user_who_is(self, nick):
        sel = self.users[nick]
        tempdict = {'rname':sel['rname'], 'addr':sel['addr'], 'chans':sel['chans'], 'connected':sel['connected']}
        return tempdict

    def channel_create(self, channel):
        if channel[0] != '#':
            channel = '#'+channel
        self.channels[channel] = {'topic':'Default topic', 'users':[]}

    def channel_delete(self, channel):
        if channel[0] != '#':
            channel = '#'+channel
        del self.channels[channel]

    def channel_get_names(self, channel):
        if channel[0] != '#':
            channel = '#'+channel
        return self.channels[channel]['users']

    def channel_who_is(self, channel):
        return self.channels[channel]


class iSPTC_Protocol(LineReceiver):
    def __init__(self, users, cid, ms_interface):
        self.name = str(cid)
        self.rname = 'None'
        self.state = "ADDUSER"
        self.users = users
        self.ms = ms_interface

    def connectionMade(self):
        self.addr = self.transport.getPeer()
        self.users[self.name] = self
        self.ms.user_add(self.name, self.addr, self)
        self.state = 'GETNAME'
        self.sendLine(welcome_message)

    def connectionLost(self, reason):
        if self.name in self.users:
            del self.users[self.name]
            print 'IR DC'

    def lineReceived(self, msg):
        if self.state == 'GETNAME':
            self.handle_GETNAME(msg)
        elif self.state == 'CHAT':
            self.handle_CHAT(msg)

    def handle_GETNAME(self, msg):
        msg = msg.split(' ')
        if msg [0] == 'NICK':
            if len(msg[1]) < nick_minlen:
                self.sendLine('NICK is too short, min length is %s' % (nick_minlen))
            elif len(msg[1]) > nick_maxlen:
                self.sendLine('NICK is too long, max length is %s' % (nick_maxlen))
            else:
                result = self.ms.user_set_nick(self.name ,msg[1])
                if result[0]:
                    self.sendLine('NICK SET %s' % (msg[1]))
                    self.name = msg[1]
                    self.state = 'CHAT'
                else:
                    self.sendLine('NICK %s :%s' % (result[1], msg[1]))
        elif msg[0] in ('JOIN', 'PRIVMSG'):
            self.sendLine('Set nick first')

    def handle_CHAT(self, msg):
        if msg[:4] == 'JOIN':
            msg = msg[5:]
            if msg[0] != '#': msg = '#'+msg
            result = self.ms.user_join_channel(self.name, msg)
            if result:
                self.sendLine('JOIN %s %s' % (msg, self.name))

        elif msg[:5] == 'LEAVE':
            msg = msg[6:]
            if msg[0] != '#': msg = '#'+msg
            self.ms.user_leave_channel(self.name, msg)
            self.sendLine('LEAVE %s %s' % (msg, self.name))

        elif msg[:4] == 'QUIT':
            reason = msg[4:]
            if reason and reason[4] != ' ':
                self.msg.user_quit(self.name, reason=msg[4:])
            else:
                self.msg.user_quit(self.name)

        elif msg[:5] == 'NAMES':
            namlist = self.ms.channel_get_names(msg[6:])
            self.sendLine('NAMES-BEGIN::'+msg[6:])
            for x in namlist:
                self.sendLine('NAMES::%s::%s' % (msg[6:], x))
            self.sendLine('NAMES-END::'+msg[6:])

        elif msg[:4] == 'NICK':
            self.handle_GETNAME(msg)

        elif msg[:3] == 'MSG':
            b = msg.find(':')
            #  or msg[:7] == 'PRIVMSG' add later
            self.ms.user_msg(self.name, msg[4:b-1], msg[b+1:])

        elif msg[:3] == 'WHO':
            if msg[4] == '#':
                result = self.ms.channel_who_is(msg[4:])
            else:
                result = self.ms.user_who_is(msg[4:])
            if result:
                self.sendLine('WHO %s %s' % (msg[4:], result))

    def privMSG(self, source, target, message):
        self.sendLine('PRIVMSG %s %s :%s' % (source, target, message))

    def joinMSG(self, source, target):
        self.sendLine('JOIN %s %s' % (source, target))

    def leaveMSG(self, source, target):
        self.sendLine('LEAVE %s %s' % (source, target))

    def quitMSG(self, source, target, reson=''):
        self.sendLine('QUIT %s %s :%s' % (source, target, reason))


class TwistedChatFactory(Factory):
    def __init__(self, users, ms_interface):
        self.users = users # maps user names to Chat instances
        self.cur_id = 0
        self.ms_interface =  ms_interface

    def buildProtocol(self, addr):
        self.cur_id += 1
        return iSPTC_Protocol(self.users, self.cur_id, self.ms_interface)

if __name__ == '__main__':
    users = {}
    ms = Master_Server(users)
    reactor.listenTCP(44672, TwistedChatFactory(users, ms))
    reactor.run()
