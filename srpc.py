import socket
from endpoint import Endpoint
from random import randint
from connection import Connection
from payload import Payload

class SRPC(object):
    """docstring for SRPC"""


    def __init__(self, port = 0):
        super(SRPC, self).__init__()
        self.port = port #default to ephemeral port assigned by OS
        self.sock = socket.socket(socket.AF_INET, # Internet
                                  socket.SOCK_DGRAM) # UDP
        self.sock.bind(('', port)) # Bind to all interfaces on port
        self.connectionTable = {}
        self.serviceTable = {}
        self.seed = randint(0, 32767)
        self.counter = 1

    def getNewSubport(self):
        self.counter += 1
        if self.counter > 32767:
            self.counter = 1
        return (self.seed & 0xFFFF) << 16 | self.counter

    def connect(self, host, port, service):
        addr = socket.gethostbyname(host)
        endpoint = Endpoint(addr, port, self.getNewSubport())
        connection = Connection(self, endpoint, None)
        self.connectionTable[endpoint] = connection
        connection.connect(service)

if __name__ == '__main__':
    srpc = SRPC(port=5001)
    data, addr = srpc.sock.recvfrom(1024)
    p = Payload(buffer=data)
    print p.toString(), "len:", len(data)
    # srpc.sock.sendto(data,
    #                  ("127.0.0.1", 5000))
    #srpc.connect("localhost", 5000, "hwdb")
