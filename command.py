
class Command:
    """docstring for Command"""
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
