import payload
from struct import calcsize, unpack, unpack_from, pack

class DataPayload(payload.Payload):
    """docstring for DataPayload"""
    def __init__(self, buffer=None, subport=0, seqno=0, command=0, fnum=0, nfrags=0, service=None, data_len=0, frag_len=0, data=None):
        super(DataPayload, self).__init__(buffer, subport, seqno, command, fnum, nfrags)
        self.data_len = data_len
        self.frag_len = frag_len
        self.data = data
        if buffer is not None:
            self.data_len, self.frag_len = unpack("HH", buffer[12:16])
            self.data = buffer[16:]


    def pack(self):
        buff = super(DataPayload, self).pack()
        buff = buff + pack("HH", self.data_len, self.frag_len) + self.data
        return buff

    def toString(self):
        return "DataPayload:\n\Data_len: {}\t Frag_len:{}\n\t{}".format(self.data_len, self.frag_len, super(DataPayload, self).toString())
