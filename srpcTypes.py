from Queue import Queue

class Service(object):
    """Provides a thread-safe FIFO for incoming messages for a named service"""
    def __init__(self, serviceName):
        self.name = serviceName
        self.messageQueue = Queue()

    def add(self, message):
        self.messageQueue.put(message, block=True)

    def query(self):
        return self.messageQueue.get(block=True)

    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Query(object):
    """Provides storage for an incoming message and related connection"""
    def __init__(self, connection, query):
        self.connection = connection
        self.query = query

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
