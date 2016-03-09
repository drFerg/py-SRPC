from struct import pack, unpack

class Payload(object):
    """docstring for Payload"""
    def __init__(self, buffer = None, subport = 0, seqno = 0, command = 0, fnum = 0, nfrags = 0):
        super(Payload, self).__init__()
        self.subport = subport
        self.seqno = seqno
        self.command = command
        self.fragment = fnum
        self.fragmentCount = nfrags
        if buffer is not None:
            #Unpack subport (host order)
            self.subport = unpack("@I", buffer[0:4])[0]
            #Upack rest (network order)
            (self.seqno, self.command, self.fragment,
            self.fragmentCount) = unpack(">IHBB", buffer[4:12])

    def pack(self):
        return pack(">IIHBB", self.subport, self.seqno, self.command,
                             self.fragment, self.fragmentCount)

    def toString(self):
        return "Payload - Subport: {}\n\tSeqNo: {}\
        \n\tCommand: {}\n\tFragment: {}\n\tFragCount: {}".format(self.subport,
               self.seqno, self.command, self.fragment, self.fragmentCount)
