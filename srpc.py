from random import randint
import socket
from threading import Thread, Timer
#SRPC imports
from connection import Connection
from payload import Payload
from srpcTypes import Service, Endpoint
from srpcDefs import SRPCDef, Command

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
        self.readerThread = Thread(target=self.reader)
        self.readerThread.start()
        self.cleanerThread = Timer(0.020, self.cleaner)
        self.cleanerThread.start()

    def getNewSubport(self):
        self.counter += 1
        if self.counter > 32767:
            self.counter = 1
        return (self.seed & 0xFFFF) << 16 | self.counter

    def connect(self, host, port, serviceName):
        address = socket.gethostbyname(host)
        endpoint = Endpoint(address, port, self.getNewSubport())
        connection = Connection(self.sock, endpoint, None)
        self.connectionTable[endpoint] = connection
        if connection.connect(serviceName):
            return connection
        else:
            return None

    def offerService(self, serviceName):
        service = Service(serviceName)
        self.serviceTable[serviceName] = service
        return service

    def lookupService(self, serviceName):
        return self.serviceTable.get(serviceName)

    def reader(self):
        while True:
            data, addr = self.sock.recvfrom(SRPCDef.FRAGMENT_SIZE * 10)
            payload = Payload(buffer=data)
            endpoint = Endpoint(addr[0], addr[1], payload.subport)
            connection = self.connectionTable.get(endpoint)
            # print "Received {} from {}:{}".format(payload.command, addr[0], addr[1])
            # print "Found connection: {}".format(connection is not None)

            if connection is not None:
                connection.commandReceived(payload)

            elif payload.command == Command.CONNECT:
                payload = ConnectPayload(buffer=data)
                service = self.serviceTable.get(payload.serviceName)

                if service is not None:
                    connection = Connection(self.sock, endpoint, service)
                    self.connectionTable[endpoint] = connection
                    connection.commandReceived(payload)

    def cleaner(self):
        for endpoint in self.connectionTable.keys():
            connection = self.connectionTable[endpoint]
            connection.checkStatus()
            if connection.isTimedOut():
                self.connectionTable.pop(endpoint)

        self.cleanerThread = Timer(0.020, self.cleaner)
        self.cleanerThread.start()


if __name__ == '__main__':
    def servHandler(service):
        while True:
            query = service.query()
            print query
            query.connection.response("OK")

    srpc = SRPC(port=5001)
    # data, addr = srpc.sock.recvfrom(1024)
    # p = Payload(buffer=data)
    # print p.toString(), "len:", len(data)
    # srpc.sock.sendto(data,
    #                  ("127.0.0.1", 5000))
    serv = srpc.offerService("handler")
    serv_t = Thread(target=servHandler, args=(serv,))
    conn = srpc.connect("localhost", 5000, "HWDB")
    if conn is None:
        SystemExit()
    print "Connected: {}".format(conn is not None)
    print "SQL:create table b (i integer, r real)"
    print conn.call("SQL:create table b (i integer, r real)")
    print conn.call("SQL:insert into b values ('5', '5.0')")
    print conn.call("BULK:72\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\n")
