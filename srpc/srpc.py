from random import randint
import socket
from threading import Thread, Timer, Event
#SRPC imports
from connection import Connection
from payload import Payload, ConnectPayload
from srpcTypes import Service, Endpoint
from srpcDefs import SRPCDef, Command

class SRPC(object):
    """A simple RPC library for connecting to and offering services"""

    def __init__(self, port = 0):
        super(SRPC, self).__init__()
        self.port = port  # default to ephemeral port assigned by OS
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)
        self.sock.bind(('', port))  # Bind to all interfaces on port
        self.port = self.sock.getsockname()[1]
        self.connectionTable = {}
        self.serviceTable = {}
        self.seed = randint(0, 32767)
        self.counter = 1
        self.stop = Event()  # Thread-safe Stop event for exiting threads
        self.readerThread = Thread(target=self.reader, args=(self.stop,))
        self.readerThread.start()
        self.cleanerThread = Timer(0.020, self.cleaner, args=(self.stop,))
        self.cleanerThread.start()

    def details(self):
        """Returns IP and port socket is bound to """
        return self.sock.getsockname()

    def close(self):
        """Close down the srpc system"""
        self.stop.set()  # Alert threads to stop using stop event
        # Send empty packet to readerThread to break it out of blocking recv
        self.sock.sendto("", self.sock.getsockname())
        self.readerThread.join()
        self.cleanerThread.join()
        self.sock.close()

    def _getNewSubport(self):
        """Private method for getting a new subport number"""
        self.counter += 1
        if self.counter > 32767:
            self.counter = 1
        return (self.seed & 0xFFFF) << 16 | self.counter

    def connect(self, host, port, serviceName):
        """Connect to a service offered at host:port
           Returns connection if successful,
           otherwise, None
        """
        address = socket.gethostbyname(host)
        endpoint = Endpoint(address, port, self._getNewSubport())
        connection = Connection(self.sock, endpoint, None)
        self.connectionTable[endpoint] = connection
        if connection.connect(serviceName):
            return connection
        else:
            return None

    def disconnect(self, connection):
        """Disconnect an existing connection, notifying the remote client"""
        connection.disconnect()
        self.connectionTable.pop(connection.source)

    def offerService(self, serviceName):
        """Offer a service (serviceName) to other remote clients"""
        service = Service(serviceName)
        self.serviceTable[serviceName] = service
        return service

    def lookupService(self, serviceName):
        """Lookup and return an offered service, if it exists"""
        return self.serviceTable.get(serviceName)

    def reader(self, stop_event):
        """Reads packets from socket and updates connections
           until stop_event is received
        """
        while not stop_event.is_set():
            data, addr = self.sock.recvfrom(SRPCDef.FRAGMENT_SIZE * 10)
            if len(data) == 0:
                break
            payload = Payload(buffer=data)
            endpoint = Endpoint(addr[0], addr[1], payload.subport)
            connection = self.connectionTable.get(endpoint)

            if connection is not None:  #Found a valid connection record
                connection.commandReceived(payload)
            elif payload.command == Command.CONNECT:
                payload = ConnectPayload(buffer=data)
                service = self.serviceTable.get(payload.serviceName)
                
                if service is not None:
                    connection = Connection(self.sock, endpoint, service)
                    self.connectionTable[endpoint] = connection
                    connection.commandReceived(payload)
            #else: invalid connection + command request

    def cleaner(self, stop_event):
        if stop_event.is_set():
            return
        for endpoint in self.connectionTable.keys():
            connection = self.connectionTable[endpoint]
            connection.checkStatus()
            if connection.isTimedOut():
                self.connectionTable.pop(endpoint)

        self.cleanerThread = Timer(0.020, self.cleaner, args=(self.stop,))
        self.cleanerThread.start()
