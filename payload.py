from struct import pack, unpack

class Payload(object):
    """docstring for Payload"""
    def __init__(self, buffer = None, subport = 0, seqno = 0, command = 0, fnum = 0, nfrags = 0):
        super(Payload, self).__init__()
        if buffer is None:
            self.subport = subport
            self.seqno = seqno
            self.command = command
            self.fnum = fnum
            self.nfrags = nfrags
        else:
            atts = unpack("iihBB", buffer[:12])
            self.subport = atts[0]
            self.seqno = atts[1]
            self.command = atts[2]
            self.fnum = atts[3]
            self.nfrags = atts[4]


    def pack(self):
        return pack("iihBB", self.subport, self.seqno, self.command,
                             self.fnum, self.nfrags)

    def toString(self):
        return "Payload - Subport: {}\n\tSeqNo: {}\
        \n\tCommand: {}\n\tFragment: {}\n\tFragCount: {}".format(self.subport,
               self.seqno, self.command, self.fnum, self.nfrags)
