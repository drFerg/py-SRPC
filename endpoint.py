

class Endpoint(object):
    """docstring for EndPoint"""
    def __init__(self, address, port, subport):
        super(Endpoint, self).__init__()
        self.address = address
        self.port = port
        self.subport = subport

    # def hashCode(self):
    #     return address ^ port ^ subport

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash((self.address, self.port, self.subport))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
        # return (self.address == other.address and
        #         self.port == self.port and
        #         self.subport == self.subport)
