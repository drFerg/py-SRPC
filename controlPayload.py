import payload

class ControlPayload(payload.Payload):
    """docstring for ControlPayload"""
    def __init__(self, buffer = None, subport = 0, seqno = 0, command = 0, fnum = 0, nfrags = 0):
        super(ControlPayload, self).__init__(buffer, subport, seqno, command, fnum, nfrags)
