from threading import Condition
from payload import ConnectPayload, ControlPayload, DataPayload
from srpcDefs import SRPCDef, Command
from srpcTypes import Query

class Connection(object):
    """Manages state for a single RPC connection to another host"""

    #SRPC states
    IDLE = 0
    QACK_SENT = 1
    RESPONSE_SENT = 2
    CONNECT_SENT = 3
    QUERY_SENT = 4
    AWAITING_RESPONSE = 5
    TIMEDOUT = 6
    DISCONNECT_SENT = 7
    FRAGMENT_SENT = 8
    FACK_RECEIVED = 9
    FACK_SENT = 10
    SEQNO_SENT = 11
    #Set of states requiring retries if to reply received
    RETRY_SET = (CONNECT_SENT, QUERY_SENT, RESPONSE_SENT, DISCONNECT_SENT,
                 FRAGMENT_SENT, SEQNO_SENT)

    def __init__(self, sock, source, service):
        """Initialise with a socket, endpoint and service name"""
        super(Connection, self).__init__()
        self.sock = sock
        self.source = source
        self.service = service
        self.state = self.IDLE
        self.ticks         = 0
        self.ticksLeft     = 0
        self.ticksTilPing  = SRPCDef.TICKS_BETWEEN_PINGS
        self.pingsTilPurge = SRPCDef.PINGS_BEFORE_PURGE
        self.nattempts     = SRPCDef.ATTEMPTS
        self.data = ""
        self.resp = ""
        self.seqNo = 0
        self.lastPayload = None
        self.lastFrag = 0
        self.cond = Condition() #Creates conditional variable with internal lock

    def resetPings(self):
        self.ticksTilPing  = SRPCDef.TICKS_BETWEEN_PINGS
        self.pingsTilPurge = SRPCDef.PINGS_BEFORE_PURGE

    def resetTicks(self):
        self.ticks     = SRPCDef.TICKS
        self.ticksLeft = SRPCDef.TICKS
        self.nattempts = SRPCDef.ATTEMPTS

    def isTimedOut(self):
        return self.state == self.TIMEDOUT

    def setState(self, newState):
        self.resetPings()
        self.cond.acquire()
        self.state = newState
        self.cond.notifyAll()
        self.cond.release()

    def waitForState(self, stateSet):
        self.cond.acquire()
        while (self.state not in stateSet):
            self.cond.wait()
        self.cond.release()

    def send(self, payload):
        self.sock.sendto(payload.pack(),
                         (self.source.address, self.source.port))
        self.lastPayload = payload

    def sendCommand(self, command):
        control = ControlPayload(self.source.subport, self.seqNo, command, 1, 1)
        self.send(control)

    def retry(self):
        if self.state in self.RETRY_SET:
            self.send(self.lastPayload)

    def ping(self):
        self.sendCommand(Command.PING)

    def checkStatus(self):
        # Retry connections which have not responded in a timely fashion
        if self.state in self.RETRY_SET:
            self.ticksLeft -= 1
            if self.ticksLeft <= 0:
                self.nattempts -= 1
                if self.nattempts <= 0:
                    self.setState(self.TIMEDOUT)
                else:
                    self.ticks *= 2
                    self.ticksLeft = self.ticks
                    self.retry()
        else: #Periodically ping idle connections
            self.ticksTilPing -= 1
            if self.ticksTilPing <= 0:
                self.pingsTilPurge -= 1
                if self.pingsTilPurge <= 0:
                    self.setState(self.TIMEDOUT)
                else:
                    self.ticksTilPing = SRPCDef.TICKS_BETWEEN_PINGS
                    self.ping()


    def connect(self, serviceName):
        self.resetTicks()
        payload = ConnectPayload(subport=self.source.subport,
                                 seqNo=self.seqNo,
                                 nfrags=1, fnum=1,
                                 serviceName=serviceName + '\0')
        self.send(payload)
        self.setState(self.CONNECT_SENT)
        self.waitForState((self.IDLE, self.TIMEDOUT))

        if self.state == self.TIMEDOUT:
            return False
        else:
            return True

    def call(self, query):
        # Check connection is ready to send
        if self.state == self.IDLE:
            #Handle seqno wrap around and synch
            if self.seqNo >= SRPCDef.SEQNO_LIMIT:
                self.seqNo = SRPCDef.SEQNO_START
                self.send(Command.SEQNO)
                self.setState(self.SEQNO_SENT)
                self.waitForState((self.IDLE, self.TIMEDOUT))
                if state == self.TIMEDOUT:
                    return None

            self.seqNo += 1

            query = query + '\0'
            qlen = len(query)
            if qlen > SRPCDef.MAX_LENGTH:
                return None
            # Calculate number of fragments and send
            fragmentCount = (qlen - 1) / SRPCDef.FRAGMENT_SIZE + 1
            fragment = 1
            while fragment < fragmentCount:
                index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
                payload = DataPayload(subport=self.source.subport, seqNo=self.seqNo,
                                      command=Command.FRAGMENT,
                                      fnum=fragment, nfrags=fragmentCount,
                                      data_len=qlen,
                                      data=query[index:index + SRPCDef.FRAGMENT_SIZE])
                self.lastFrag = fragment
                self.send(payload)

                self.setState(self.FRAGMENT_SENT)
                self.waitForState((self.TIMEDOUT, self.FACK_RECEIVED))
                if self.state == self.TIMEDOUT:
                    return None
                fragment += 1

            #Send last fragment
            index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
            payload = DataPayload(subport=self.source.subport, seqNo=self.seqNo,
                                  command=Command.QUERY,
                                  fnum=fragment, nfrags=fragmentCount,
                                  data_len=qlen, data=query[index:])

            self.send(payload)
            self.resetTicks()
            self.setState(self.QUERY_SENT)
            self.waitForState((self.TIMEDOUT, self.IDLE))
            return self.resp

        else:
            return None


    def response(self, query):
        if self.state == self.QACK_SENT:
            query = query + '\0'
            qlen = len(query)
            if qlen > MAX_LENGTH:
                return False

            fragmentCount = (qlen - 1) / SRPCDef.FRAGMENT_SIZE + 1
            while fragment < fragmentCount:
                index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
                payload = DataPayload(subport=self.source.subport, seqNo=self.seqNo,
                                      command=Command.FRAGMENT,
                                      fnum=fragment, nfrags=fragmentCount,
                                      data_len=qlen,
                                      data=query[index:index + SRPCDef.FRAGMENT_SIZE])
                self.lastFrag = fragment
                self.send(payload)

                self.setState(self.FRAGMENT_SENT)
                self.waitForState((self.TIMEDOUT, self.FACK_RECEIVED))
                if self.state == self.TIMEDOUT:
                    return False
                fragment += 1
            #Send last fragment
            index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
            payload = DataPayload(subport=self.source.subport, seqNo=self.seqNo,
                                  command=Command.RESPONSE,
                                  fnum=fragment, nfrags=fragmentCount,
                                  data_len=qlen, data=query[index:])

            self.send(payload)
            self.resetTicks()
            self.setState(self.RESPONSE_SENT)
            return True
        else:
            return False


    def disconnect(self):
        self.sendCommand(Command.DISCONNECT)
        self.waitForState((self.TIMEDOUT,))

    def SACKReceived(self, payload):
        if self.state == self.SEQNO_SENT:
            setState(self.IDLE)

    def SEQNOReceived(self, payload):
        if self.state in (self.IDLE, self.AWAITING_RESPONSE):
            self.resetTicks()
            self.send(Command.SACK)
            self.seqNo = payload.seqNo
            self.setState(self.IDLE)

    def RACKReceived(self, payload):
        if self.seqNo == payload.seqNo:
            self.setState(self.IDLE)

    def RESPONSEReceived(self, payload):
        payload = DataPayload(buffer=payload.buffer)
        if payload.seqNo != self.seqNo:
            return
        if self.state in (self.QUERY_SENT, self.AWAITING_RESPONSE):
            self.resp = payload.data
        elif (payload.seqNo == self.seqNo and self.state == self.FACK_SENT and
              (payload.fragment - self.lastFrag) == 1 and
            payload.fragmentCount == payload.fragment):
            self.resp = self.data + payload.data
            data = ""
        else:
            return
        self.resetTicks()
        self.send(ControlPayload(self.source.subport, self.seqNo, Command.RACK,
                                 payload.fragment, payload.fragmentCount))

        self.setState(self.IDLE)

    def QACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(self.AWAITING_RESPONSE)

    def QUERYReceived(self, payload):
        payload = DataPayload(buffer=payload.buffer)
        if (payload.seqNo - seqNo) == 1 and self.state in (self.IDLE,
                                                         self.RESPONSE_SENT):
            self.seqNo = payload.seqNo
            query = payload.getData
        elif (payload.seqNo == self.seqNo and
              self.state in (self.QACK_SENT, self.RESPONSE_SENT)):
            self.retry()
            return
        else:
            return

        self.send(ControlPayload(self.source.subport, self.seqNo, Command.QACK,
                                 payload.fragment, payload.fragmentCount))
        self.setState(self.QACK_SENT)
        self.service.add(Query(self, query))

    def FACKReceived(self, payload):
        if (payload.seqNo == self.seqNo and self.state == self.FRAGMENT_SENT
            and payload.fragment == self.lastFrag):
            self.setState(self.FACK_RECEIVED)

    def FRAGMENTReceived(self, payload):
        payload = DataPayload(buffer=payload.buffer)
        isQ = (self.state in (self.IDLE, self.RESPONSE_SENT) and
              (payload.seqNo - self.seqNo) == 1 and payload.fragment == 1)
        isR = (self.state in (self.QUERY_SENT, self.AWAITING_RESPONSE) and
              payload.seqNo == self.seqNo and payload.fragment == 1)

        if (isQ or isR): #New fragment set
            self.data = payload.data
            self.seqNo = payload.seqNo
        elif payload.seqNo == self.seqNo and self.state == self.FACK_SENT:
            if (payload.fragment - self.lastFrag) == 1: #Next fragment
                self.data = self.data + payload.data
            elif payload.fragment == self.lastFrag: #Old fragment
                self.retry()
                return
            else:
                return
        else:
            return

        self.lastFrag = payload.fragment
        self.send(ControlPayload(self.source.subport, self.seqNo, Command.FACK,
                                 payload.fragment, payload.fragmentCount))
        self.setState(self.FACK_SENT)

    def DACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(self.TIMEDOUT)

    def DISCONNECTReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.send(Command.DACK)
            self.setState(self.TIMEDOUT)

    def CACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(self.IDLE)

    def CONNECTReceived(self, payload):
        self.seqNo = payload.seqNo
        self.send(Command.CACK)
        self.setState(self.IDLE)
        self.resetTicks()

    def PINGReceived(self, payload):
        self.sendCommand(Command.PACK)

    def PACKReceived(self, payload):
        self.resetPings()

    #Switch-table dictionary for received commands
    # (requires all functions to take payload)
    commandsList = (CONNECTReceived,
                    CACKReceived,
                    QUERYReceived,
                    QACKReceived,
                    RESPONSEReceived,
                    RACKReceived,
                    DISCONNECTReceived,
                    DACKReceived,
                    FRAGMENTReceived,
                    FACKReceived,
                    PINGReceived,
                    PACKReceived,
                    SEQNOReceived,
                    SACKReceived,
                    )

    def commandReceived(self, payload):
        Connection.commandsList[payload.command - 1](self, payload)
