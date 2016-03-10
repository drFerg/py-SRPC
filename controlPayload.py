import payload

class ControlPayload(payload.Payload):
    """docstring for ControlPayload"""
    def __init__(self, subport = 0, seqNo = 0, command = 0, fnum = 0, nfrags = 0, buffer = None):
        super(ControlPayload, self).__init__(subport, seqNo, command, fnum, nfrags, buffer)
