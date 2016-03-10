from Queue import Queue

class Service(object):

    def __init__(self, serviceName):
        self.name = serviceName
        self.messageQueue = Queue()


    def add(self, message):
        self.messageQueue.put(message, block=True)

    def query(self):
        return self.messageQueue.get(block=True)
