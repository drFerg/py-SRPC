

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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
