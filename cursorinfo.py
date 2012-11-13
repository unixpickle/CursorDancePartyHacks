import json

class CursorInfo:
    """ A class which represents a cursor description on cursor dance party. """
    def __init__(self, x, y, angle, scale, cursor, rotations):
        self.x, self.y, self.scale = x, y, scale
        self.angle = angle
        self.cursor, self.rotations = cursor, rotations

    @staticmethod
    def from_json(s):
        mainDict = json.loads(s)
        theDict = mainDict['args'][0]
        return CursorInfo.from_dict(theDict)

    @staticmethod
    def from_dict(theDict):
        x = theDict['x']
        y = theDict['y']
        scale = theDict['scale']
        cursor = theDict['cursor']
        rotations = theDict['rotations']
        angle = theDict['angle']
        return CursorInfo(x, y, angle, scale, cursor, rotations)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        theDict = {'x': self.x,
                   'y': self.y,
                   'scale': self.scale,
                   'cursor': self.cursor,
                   'rotations': self.rotations,
                   'angle': self.angle};
        return theDict

    def to_message(self):
        cDict = self.to_dict()
        message = {'name': 'mouse-coords', 'args': [cDict]}
        return '5:::' + json.dumps(message)

class ClientCursorInfo:
    """ The cursor info from a client. Includes identifier """
    def __init__(self, anId, info):
        self.id = anId
        self.info = info

    @staticmethod
    def from_json(s):
        mainDict = json.loads(s)
        if mainDict['name'] != 'mouse-coords': return None
        theDict = mainDict['args'][0]['mouse']
        info = CursorInfo.from_dict(theDict)
        ident = mainDict['args'][0]['id']
        return ClientCursorInfo(ident, info)

def encode_set_cursor_info(info):
    """ This exists for backwards compatibility for .to_message() """
    cDict = info.to_dict()
    message = {'name': 'mouse-coords', 'args': [cDict]}
    return '5:::' + json.dumps(message)

def decode_client_cursor_info(info):
    return ClientCursorInfo.from_json(info)

