from threading import Condition
from state import State
from payload import ConnectPayload, ControlPayload, DataPayload
from command import Command
from srpcdefs import SRPCDef
from query import Query

class Connection(object):
    """docstring for Connection"""
    def __init__(self, sock, source, service):
        super(Connection, self).__init__()
        self.sock = sock
        self.source = source
        self.service = service
        self.state = State.IDLE
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
        return self.state == State.TIMEDOUT

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
        # sleep on state

    def send(self, payload):
        self.sock.sendto(payload.pack(),
                         (self.source.address, self.source.port))
        self.lastPayload = payload

    def sendCommand(self, command):
        control = ControlPayload(self.source.subport, self.seqNo, command, 1, 1)
        self.send(control)

    def retry(self):
        if self.state in State.RETRY_SET:
            self.send(self.lastPayload)

    def ping(self):
        self.sendCommand(Command.PING)

    def checkStatus(self):
        # Retry connections which have not responded in a timely fashion
        if self.state in State.RETRY_SET:
            self.ticksLeft -= 1
            if self.ticksLeft <= 0:
                self.nattempts -= 1
                if self.nattempts <= 0:
                    self.setState(State.TIMEDOUT)
                else:
                    self.ticks *= 2
                    self.ticksLeft = self.ticks
                    self.retry()
        else: #Periodically ping idle connections
            self.ticksTilPing -= 1
            if self.ticksTilPing <= 0:
                self.pingsTilPurge -= 1
                if self.pingsTilPurge <= 0:
                    self.state = State.TIMEDOUT
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
        self.setState(State.CONNECT_SENT)
        self.waitForState((State.IDLE, State.TIMEDOUT))

        if self.state == State.TIMEDOUT:
            return False
        else:
            return True

    def call(self, query):
        # Check connection is ready to send
        if self.state == State.IDLE:
            #Handle seqno wrap around and synch
            if self.seqNo >= SRPCDef.SEQNO_LIMIT:
                self.seqNo = SRPCDef.SEQNO_START
                self.send(Command.SEQNO)
                self.setState(State.SEQNO_SENT)
                self.waitForState((State.IDLE, State.TIMEDOUT))
                if state == State.TIMEDOUT:
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

                self.setState(State.FRAGMENT_SENT)
                self.waitForState((State.TIMEDOUT, State.FACK_RECEIVED))
                if self.state == State.TIMEDOUT:
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
            self.setState(State.QUERY_SENT)
            self.waitForState((State.TIMEDOUT, State.IDLE))
            return self.resp

        else:
            return None


    def response(self, query):
        if self.state == State.QACK_SENT:
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

                self.setState(State.FRAGMENT_SENT)
                self.waitForState((State.TIMEDOUT, State.FACK_RECEIVED))
                if self.state == State.TIMEDOUT:
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
            self.setState(State.RESPONSE_SENT)
            return True
        else:
            return False


    def disconnect(self, payload):
        self.send(Command.DISCONNECT)
        self.waitForState((State.TIMEDOUT))

    def SACKReceived(self, payload):
        if self.state == State.SEQNO_SENT:
            setState(State.IDLE)

    def SEQNOReceived(self, payload):
        if self.state in (State.IDLE, State.AWAITING_RESPONSE):
            self.resetTicks()
            self.send(Command.SACK)
            self.seqNo = payload.seqNo
            self.setState(State.IDLE)

    def RACKReceived(self, payload):
        if self.seqNo == payload.seqNo:
            self.setState(State.IDLE)

    def RESPONSEReceived(self, payload):
        payload = DataPayload(buffer=payload.buffer)
        if payload.seqNo != self.seqNo:
            return
        if self.state in (State.QUERY_SENT, State.AWAITING_RESPONSE):
            self.resp = payload.data
        elif (payload.seqNo == self.seqNo and self.state == State.FACK_SENT and
              (payload.fragment - self.lastFrag) == 1 and
            payload.fragmentCount == payload.fragment):
            self.resp = self.data + payload.data
            data = ""
        else:
            return
        self.resetTicks()
        self.send(ControlPayload(self.source.subport, self.seqNo, Command.RACK,
                                 payload.fragment, payload.fragmentCount))

        self.setState(State.IDLE)

    def QACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(State.AWAITING_RESPONSE)

    def QUERYReceived(self, payload):
        payload = DataPayload(buffer=payload.buffer)
        if (payload.seqNo - seqNo) == 1 and self.state in (State.IDLE,
                                                         State.RESPONSE_SENT):
            self.seqNo = payload.seqNo
            query = payload.getData
        elif (payload.seqNo == self.seqNo and
              self.state in (State.QACK_SENT, State.RESPONSE_SENT)):
            self.retry()
            return
        else:
            return

        self.send(ControlPayload(self.source.subport, self.seqNo, Command.QACK,
                                 payload.fragment, payload.fragmentCount))
        self.setState(State.QACK_SENT)
        self.service.add(Query(self, query))

    def FACKReceived(self, payload):
        if (payload.seqNo == self.seqNo and self.state == State.FRAGMENT_SENT
            and payload.fragment == self.lastFrag):
            self.setState(State.FACK_RECEIVED)

    def FRAGMENTReceived(self, payload):
        payload = DataPayload(buffer=payload.buffer)
        isQ = (self.state in (State.IDLE, State.RESPONSE_SENT) and
              (payload.seqNo - self.seqNo) == 1 and payload.fragment == 1)
        isR = (self.state in (State.QUERY_SENT, State.AWAITING_RESPONSE) and
              payload.seqNo == self.seqNo and payload.fragment == 1)

        if (isQ or isR): #New fragment set
            self.data = payload.data
            self.seqNo = payload.seqNo
        elif payload.seqNo == self.seqNo and self.state == State.FACK_SENT:
            if (payload.fragment - self.lastFrag) == 1: #Next fragment
                self.data = self.data + payload.data
            elif  payload.fragment == self.lastFrag: #Old fragment
                self.retry()
                return
            else:
                return
        else:
            return

        self.lastFrag = payload.fragment
        self.send(ControlPayload(self.source.subport, self.seqNo, Command.FACK,
                                 payload.fragment, payload.fragmentCount))
        self.setState(State.FACK_SENT)

    def DACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(State.TIMEDOUT)

    def DISCONNECTReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.send(Command.DACK)
            self.setState(State.TIMEDOUT)

    def CACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(State.IDLE)

    def CONNECTReceived(self, payload):
        self.seqNo = payload.seqNo
        self.send(Command.CACK)
        self.setState(State.IDLE)
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
