import httplib2
import time
import websocket
import threading
from collections import deque

class SocketIO:
    def __init__(self, baseURL, callback):
        self.base = baseURL
        self.callback = callback
        self.writeQueue = deque()
        self.writeLock = threading.Lock()
        self.dieLock = threading.Lock()

    def start(self):
        try:
            self.ws = open_websocket(self.base)
            self.killEvent = threading.Event()
            rThread = threading.Thread(target=self.listenThread)
            wThread = threading.Thread(target=self.sendThread)
            rThread.setDaemon(True)
            wThread.setDaemon(True)
            rThread.start()
            wThread.start()
            return True
        except:
            return False

    def stop(self):
        self.dieLock.acquire()
        self.killEvent.set()
        self.ws.close()
        self.dieLock.release()

    def send(self, message):
        self.writeLock.acquire()
        self.writeQueue.append(message)
        self.writeLock.release()

    def listenThread(self):
        while 1:
            buff = None
            if self.killEvent.isSet(): return
            try:
                buff = self.ws.recv()
            except Exception, e:
                self.handleIOFailed()
                return
            self.handleRecv(buff)

    def sendThread(self):
        while 1:
            if self.killEvent.isSet(): return
            self.writeLock.acquire()
            nextPacket = None
            if len(self.writeQueue) > 0:
                nextPacket = self.writeQueue.popleft()
            self.writeLock.release()
            if nextPacket:
                try:
                    self.ws.send(nextPacket)
                except:
                    self.handleIOFailed()
                    return
            else: time.sleep(0.01)

    def handleRecv(self, buf):
        numColons = 0
        initLen = 0
        for x in buf:
            if x == ':': numColons += 1
            initLen += 1
            if numColons == 3: break
        header = buf[:initLen]
        remainder = buf[initLen:]
        t = buf[0]
        if t == '0': self.stop()
        elif t == '2': self.send('2:::')
        else: self.callback(True, t, remainder)

    def handleIOFailed():
        self.dieLock.acquire()
        if not self.killEvent.isSet():
            self.ws.close()
            self.killEvent.set()
            self.callback(False)
        self.dieLock.release()

def request_url_part(baseURL):
	h = httplib2.Http();
	timeStr = str(int(time.mktime(time.gmtime()) * 1000))
	initUrl = 'http://' + baseURL + '/?t=' + timeStr
	resp, content = h.request(initUrl, 'GET')
	return extract_url_part(content)

def extract_url_part(content):
	str = ''
	for x in range(0, len(content)):
		if content[x] == ':': break
		else: str += content[x]
	return str

def generate_websockets_url(baseURL):
	urlPart = extract_url_part(request_url_part(baseURL))
	return 'ws://' + baseURL + '/websocket/' + urlPart

def open_websocket(base):
    return websocket.create_connection(generate_websockets_url(base))

def is_data_req(s):
    return s[:4] == '5:::'

