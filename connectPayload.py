import payload
from struct import calcsize, unpack, unpack_from
from command import Command

class ConnectPayload(payload.Payload):
    """docstring for ConnectPayload"""
    def __init__(self, subport = 0, seqNo = 0, fnum = 0, nfrags = 0,
                 serviceName = None, buffer = None):
        super(ConnectPayload, self).__init__(subport, seqNo, Command.CONNECT, fnum, nfrags, buffer)
        if buffer is None:
            self.serviceName = serviceName
        else:
            ser_len = len(buffer) - 12
            fmt = ">{}s".format(ser_len)
            self.serviceName = unpack(fmt, buffer[12:])[0]

    def pack(self): #Pack payload and append serviceName
        return super(ConnectPayload, self).pack() + self.serviceName

    def toString(self):
        return "ConnectPayload:\n\tService: {}\n\t{}".format(self.serviceName, super(ConnectPayload, self).toString())
