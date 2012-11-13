from socketio import open_websocket, is_data_req
import cursorinfo
import time
import math

base = 'cursordanceparty.com/socket.io/1'
ws = open_websocket(base)

lastTime = int(round(time.time() * 1000))
angle = 0
while 1:
    now = int(round(time.time() * 1000))
    duration = now - lastTime
    lastTime = now
    angle += float(duration) * (360.0 / 3000.0)
    while angle > 360: angle -= 360

    yVal = (math.sin(math.radians(angle)) + 1) / 2
    xVal = (math.cos(math.radians(angle)) + 1) / 2
    inf = cursorinfo.CursorInfo(xVal, yVal, 0, 1, 1, 0)
    print cursorinfo.encode_set_cursor_info(inf)
    ws.send(cursorinfo.encode_set_cursor_info(inf))
    time.sleep(0.05)
