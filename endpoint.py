

class Endpoint(object):
    """Used as a key for identifying a connection to the RPC system"""
    def __init__(self, address, port, subport):
        super(Endpoint, self).__init__()
        self.address = address
        self.port = port
        self.subport = subport

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash((self.address, self.port, self.subport))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
