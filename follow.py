import sys
import socketio
import cursorinfo
import time
import logging
import json
import threading

logging.basicConfig(level=logging.DEBUG)

class UserFollower:
    """ A connection to the site which follows a user id """

    def __init__(self, userId, mainCallback):
        base = 'cursordanceparty.com/socket.io/1'
        self.userId = userId
        self.sock = socketio.SocketIO(base, self.callback)
        self.sock.start()
        self.mainCallback = mainCallback

    def callback(self, isOpen, typeNum='', data=None):
        if not isOpen:
            logging.error('received unexpected close')
            self.mainCallback(self)
            return
        if typeNum != '5': return

        msg = json.loads(data)
        if msg['name'] == 'mouse-coords':
            inf = cursorinfo.decode_client_cursor_info(data)
            if inf.id == self.userId:
                self.sock.send(inf.info.to_message())
                logging.info('mirroring mouse movement')
        elif msg['name'] == 'partier-left':
            partierId = msg['args'][0]['id']
            if partierId == self.userId:
                logging.info('mouse client disconnected')
                self.sock.stop()
                self.mainCallback(self)

class MainListener:
    """ A client which waits for other users and follows them """

    def __init__(self):
        self.followers = list()
        self.followersLock = threading.Lock()
        self.ignoreNext = False

    def connect(self):
        """ Reconnects the listener.
            
            This should not be called externally more than once.
        """
        base = 'cursordanceparty.com/socket.io/1'
        self.sock = socketio.SocketIO(base, self.callback)
        self.sock.start()

    def callback(self, isOpen, t='', data=None):
        if not isOpen:
            logging.error('main listener disconnected!')
            self.connect()
            return
        if t != '5': return
        msg = json.loads(data)
        if msg['name'] == 'partier-joined':
            if self.ignoreNext:
                self.ignoreNext = False
                return
            self.ignoreNext = True
            partier = msg['args'][0]['id']
            logging.info('partier joined: ' + partier)
            follower = UserFollower(partier, self.followerClosed)
            self.followersLock.acquire()
            self.followers.append(follower)
            self.followersLock.release()

    def followerClosed(self, follower):
        logging.info('removing follower')
        self.followersLock.acquire()
        self.followers.remove(follower)
        self.followersLock.release()

listener = MainListener()
listener.connect()
while 1:
    try:
        time.sleep(0.01)
    except KeyboardInterrupt:
        break
