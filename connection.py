import socket
from state import State
from connectPayload import ConnectPayload
from threading import Condition, Lock
from command import Command
from srpcdefs import SRPCDef

class Connection(object):
    SEQNO_LIMIT = 1000000000;
    SEQNO_START = 0;
    MAX_LENGTH  = 65535;
    """docstring for Connection"""
    def __init__(self, context, source, service):
        super(Connection, self).__init__()
        self.context = context
        self.source = source
        self.service = service
        self.ticks         = 0
        self.ticksLeft     = 0
        self.ticksTilPing  = SRPCDef.TICKS_BETWEEN_PINGS
        self.pingsTilPurge = SRPCDef.PINGS_BEFORE_PURGE
        self.nattempts     = SRPCDef.ATTEMPTS
        self.sock = socket.socket(socket.AF_INET, # Internet
                                  socket.SOCK_DGRAM) # UDP
        self.data = ""
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

    def waitForState(self, set):
        self.cond.acquire()
        while (self.state not in set):
            self.cond.wait()
        self.cond.release()
        # sleep on state

    def send(self, payload):
        self.sock.sendto(payload.pack(),
                         (self.source.address, self.source.port))
        self.lastPayload = payload

    def sendCommand(self, command):
        control = ControlPayload(command, self.source.subport, seqNo, 1, 1)
        self.send(control)

    def retry(self):
        if self.state in State.RETRY_SET:
            self.send(lastPayload)

    def ping(self):
        sendCommand(Command.PING)

    def checkStatus(self):
        # Retry connections which have not responded in a timely fashion
        if self.state in State.RETRY_SET:
            self.ticksLeft -= 1
            if self.ticksLeft <= 0:
                self.nattempts -= 1
                if self.nattempts <= 0:
                    self.State = State.TIMEDOUT
                else:
                    self.ticks *= 2
                    self.ticksLeft = ticks
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
                                 seqno=self.seqNo,
                                 nfrags=1, fnum=1,
                                 service=serviceName + '\0')
        print payload.toString(), len(payload.pack())
        self.send(payload)
        self.setState(State.CONNECT_SENT)
        self.waitForState((State.IDLE, State.TIMEDOUT))

        if state == State.TIMEDOUT:
            return False
        else:
            return True

    def call(self, query):
        # Check connection is ready to send
        if self.state == State.IDLE:
            #Handle seqno wrap around and synch
            if self.seqNo >= SEQNO_LIMIT:
                self.seqNo = SEQNO_START
                self.send(Command.SEQNO)
                self.setState(State.SEQNO_SENT)
                self.waitForState((State.IDLE, State.TIMEDOUT))
                if state == State.TIMEDOUT:
                    return False

            self.seqNo += 1

            query = query + '\0'
            qlen = len(query)
            if qlen > MAX_LENGTH:
                return False
            # Calculate number of fragments and send
            fragmentCount = (qlen - 1) / SRPCDef.FRAGMENT_SIZE + 1
            for fragment in range(1, fragmentCount):
                index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
                payload = DataPayload(Command.FRAGMENT, self.source.subport,
                                      self.seqNo, fragment, fragmentCount,
                                      qlen,
                                      query[index:index + SRPCDef.FRAGMENT_SIZE])
                lastFrag = fragment
                self.send(payload)

                self.setState(State.FRAGMENT_SENT)
                self.waitForState((State.TIMEDOUT, State.FACK_RECEIVED))
                if self.state == State.TIMEDOUT:
                    return False
            #Send last fragment
            index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
            payload = DataPayload(Command.QUERY, self.source.subport, self.seqNo,
                                 fragment, fragmentCount, qlen, query[index:])
            self.send(payload)
            self.resetTicks()
            self.setState(State.QUERY_SENT)
            self.waitForState((State.TIMEDOUT, State.IDLE))
            return self.response

        else:
            return False


    def response(self, query):
        if self.state == State.QACK_SENT:
            query = query + '\0'
            qlen = len(query)
            if qlen > MAX_LENGTH:
                return False

            fragmentCount = (qlen - 1) / SRPCDef.FRAGMENT_SIZE + 1
            for fragment in range(1, fragmentCount):
                index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
                payload = DataPayload(Command.FRAGMENT, self.source.subport,
                                      self.seqNo, fragment, fragmentCount,
                                      qlen,
                                      query[index:index + SRPCDef.FRAGMENT_SIZE])
                lastFrag = fragment
                self.send(payload)

                self.setState(State.FRAGMENT_SENT)
                self.waitForState((State.TIMEDOUT, State.FACK_RECEIVED))
                if self.state == State.TIMEDOUT:
                    return False
            #Send last fragment
            index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
            payload = DataPayload(Command.RESPONSE, self.source.subport, self.seqNo,
                                 fragment, fragmentCount, qlen, query[index:])
            #Send last fragment
            index = SRPCDef.FRAGMENT_SIZE * (fragment - 1)
            payload = DataPayload(Command.QUERY, self.source.subport, self.seqNo,
                                 fragment, fragmentCount, qlen, query[index:])
            self.send(payload)
            self.resetTicks()
            self.setState(State.RESPONSE_SENT)
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
        if payload.seqNo != self.seqNo:
            return
        if self.state in (State.QUERY_SENT, State.AWAITING_RESPONSE):
            self.response = payload.data
        elif (payload.seqNo == self.seqNo and self.state == State.FACK_SENT and
              (payload.fragment - self.lastFrag) == 1 and
            payload.fragmentCount == payload.fragment):
            self.response = self.data + payload.data
            data = ""
        else:
            return
        self.resetTicks()
        self.send(Command.RACK, payload.fragment, payload.fragmentCount)
        self.setState(State.IDLE)

    def QACKReceived(self, payload):
        if payload.seqNo == self.seqNo:
            self.setState(State.AWAITING_RESPONSE)

    def QUERYReceived(self, payload):
        if (payload.seqNo - seqNo) == 1 and self.state in (State.IDLE,
                                                         State.RESPONSE_SENT):
            self.seqNo = payload.seqNo
            query = payload.getData
        elif payload.seqNo == self.seqNo and self.state in (State.QACK_SENT,
                                                            State.RESPONSE_SENT):
            self.retry()
            return
        else:
            return

        self.send(Command.QACK, payload.fragment, payload.fragmentCount)
        self.setState(State.QACK_SENT)
        #service.add(query)

    def FACKReceived(self, payload):
        if (payload.seqNo == self.seqNo and self.state == State.FRAGMENT_SENT
            and payload.fragment == self.lastFrag):
            self.setState(State.FACK_RECEIVED)

    def FRAGMENTReceived(self, payload):
        isQ = (self.state in (State.IDLE, State.RESPONSE_SENT) and
              (payload.seqNo - self.seqNo) == 1 and payload.fragment == 1)
        isR = (self.state in (State.QUERY_SENT, State.AWAITING_RESPONSE) and
              payload.seqNo == self.seqNo and payload.fragment == 1)

        if (isQ or isR): #New fragment set
            self.data = payload.data
            self.seqNo = payload.seqNo
        elif payload.seqNo == self.seqNo and self.state == State.FACK_SENT:
            if (payload.fragment - lastFrag) == 1: #Next fragment
                self.data = data + payload.data
            elif  payload.fragment == lastFrag: #Old fragment
                self.retry()
                return
            else:
                return
        else:
            return

        self.lastFrag = payload.fragment
        self.send(Command.FACK, payload.fragment, payload.fragmentCount)
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
        self.send(Command.PACK)

    def PACKReceived(self, payload):
        self.resetPings()

    #Switch-table dictionary for received commands
    # (requires all functions to take payload)
    commands = {Command.CONNECT: CONNECTReceived,
                Command.CACK: CACKReceived,
                Command.DISCONNECT: DISCONNECTReceived,
                Command.DACK: DACKReceived,
                Command.FRAGMENT: FRAGMENTReceived,
                Command.FACK: FACKReceived,
                Command.QUERY: QUERYReceived,
                Command.QACK: QACKReceived,
                Command.RESPONSE: RESPONSEReceived,
                Command.RACK: RACKReceived,
                Command.PING: PINGReceived,
                Command.PACK: PACKReceived,
                Command.SEQNO: SEQNOReceived,
                Command.SACK: SACKReceived,
                }

    commandsList = (CONNECTReceived,
                CACKReceived,
                DISCONNECTReceived,
                DACKReceived,
                FRAGMENTReceived,
                FACKReceived,
                QUERYReceived,
                QACKReceived,
                RESPONSEReceived,
                RACKReceived,
                PINGReceived,
                PACKReceived,
                SEQNOReceived,
                SACKReceived,
                )

    def commandReceived(self, payload):
        commandsList[payload.command - 1](payload)
