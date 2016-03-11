from struct import pack, unpack
from command import Command

class Payload(object):
    """docstring for Payload"""
    def __init__(self, subport = 0, seqNo = 0, command = 0, fnum = 0, nfrags = 0,
                 buffer = None):
        super(Payload, self).__init__()
        self.buffer = buffer
        self.subport = subport
        self.seqNo = seqNo
        self.command = command
        self.fragment = fnum
        self.fragmentCount = nfrags
        if buffer is not None:
            #Unpack subport (host order)
            self.subport = unpack("@I", buffer[0:4])[0]
            #Upack rest (network order)
            (self.seqNo, self.command, self.fragment,
            self.fragmentCount) = unpack(">IHBB", buffer[4:12])

    def pack(self):
        return pack("@I", self.subport) + pack(">IHBB", self.seqNo, self.command,
                             self.fragment, self.fragmentCount)

    def toString(self):
        return "Payload - Subport: {}\n\tSeqNo: {}\
        \n\tCommand: {}\n\tFragment: {}\n\tFragCount: {}".format(self.subport,
               self.seqNo, self.command, self.fragment, self.fragmentCount)

class ControlPayload(Payload):
    """docstring for ControlPayload"""
    def __init__(self, subport = 0, seqNo = 0, command = 0, fnum = 0,
                 nfrags = 0, buffer = None):
        super(ControlPayload, self).__init__(subport, seqNo, command, fnum,
                                             nfrags, buffer)

class ConnectPayload(Payload):
    """docstring for ConnectPayload"""
    def __init__(self, subport = 0, seqNo = 0, fnum = 0, nfrags = 0,
                 serviceName = None, buffer = None):
        super(ConnectPayload, self).__init__(subport, seqNo, Command.CONNECT,
                                             fnum, nfrags, buffer)
        if buffer is None:
            self.serviceName = serviceName
        else:
            ser_len = len(buffer) - 12
            fmt = ">{}s".format(ser_len)
            self.serviceName = unpack(fmt, buffer[12:])[0]

    def pack(self): #Pack payload and append serviceName
        return super(ConnectPayload, self).pack() + self.serviceName

    def toString(self):
        return "ConnectPayload:\n\tService: {}\n\t{}".format(
                    self.serviceName, super(ConnectPayload, self).toString())

class DataPayload(Payload):
    """docstring for DataPayload"""
    def __init__(self, subport=0, seqNo=0, command=0, fnum=0, nfrags=0,
                 service=None, data_len=0, frag_len=0, data="", buffer=None):
        super(DataPayload, self).__init__(subport, seqNo, command, fnum, nfrags,
                                          buffer)
        self.data_len = data_len
        self.frag_len = len(data)
        self.data = data
        if buffer is not None:
            self.data_len, self.frag_len = unpack(">HH", buffer[12:16])
            self.data = buffer[16:]


    def pack(self):
        buff = super(DataPayload, self).pack()
        buff = buff + pack(">HH", self.data_len, self.frag_len) + self.data
        return buff

    def toString(self):
        return "DataPayload:\n\Data_len: {}\t Frag_len:{}\n\t{}".format(
            self.data_len, self.frag_len, super(DataPayload, self).toString())
