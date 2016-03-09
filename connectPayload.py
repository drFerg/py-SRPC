import payload
from struct import calcsize, unpack, unpack_from
from command import Command

class ConnectPayload(payload.Payload):
    """docstring for ConnectPayload"""
    def __init__(self, buffer = None, subport = 0, seqno = 0, fnum = 0, nfrags = 0, service = None):
        super(ConnectPayload, self).__init__(buffer, subport, seqno, Command.CONNECT, fnum, nfrags)
        if buffer is None:
            self.service = service
        else:
            ser_len = len(buffer) - 12
            fmt = ">{}s".format(ser_len)
            self.service = unpack(fmt, buffer[12:])[0]

    def pack(self):
        buff = super(ConnectPayload, self).pack()
        buff = buff + self.service

        return buff

    def toString(self):
        return "ConnectPayload:\n\tService: {}\n\t{}".format(self.service, super(ConnectPayload, self).toString())
