import sys
import getopt
from srpc import SRPC

def usage():
    print "python echoClient.py [-h host] [-p port] [-s service]"

def main(argv):
    host = "localhost"
    port = "20000"
    service = "Echo"

    try:
        opts, args = getopt.getopt(argv, "h:p:s:", ["host=", "port=",
                                                  "service=", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("--help"):
            usage()
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-s", "--service"):
            service = arg

    srpc = SRPC()
    conn = srpc.connect(host, int(port), service)

    if conn is None:
        print "Failure to connect to {} at {}:{}".format(service, host, port)
        sys.exit(-1)
    msg = raw_input("Send: ")
    while msg:
        resp = conn.call("ECHO:" + msg)
        if resp[0] is not '1':
            print "Echo server returned ERROR"
            break
        print "Reply: {}".format(resp[1:])
        msg = raw_input("Send: ")
    srpc.disconnect(conn)
    srpc.close()
    sys.exit(0)



if __name__ == '__main__':
    main(sys.argv[1:])
