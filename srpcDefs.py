
class SRPCDef:
    """SRPC defines"""
    TICK_LENGTH         = 20
    FRAGMENT_SIZE       = 1024
    TICKS               = 2
    ATTEMPTS            = 7;
    TICKS_BETWEEN_PINGS = (60 * 50)
    PINGS_BEFORE_PURGE  = 3
    SEQNO_LIMIT = 1000000000
    SEQNO_START = 0
    MAX_LENGTH  = 65535

class Command:
    """SRPC command codes"""
    ERROR = 0
    CONNECT = 1
    CACK = 2
    QUERY = 3
    QACK = 4
    RESPONSE = 5
    RACK = 6
    DISCONNECT = 7
    DACK = 8
    FRAGMENT = 9
    FACK = 10
    PING = 11
    PACK = 12
    SEQNO = 13
    SACK = 14
    CMD_LOW = CONNECT
    CMD_HIGH = SACK

class State:
    """SRPC state codes"""
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

    RETRY_SET = (CONNECT_SENT, QUERY_SENT, RESPONSE_SENT, DISCONNECT_SENT,
                 FRAGMENT_SENT, SEQNO_SENT)
