import sys
import getopt
from threading import Thread

from srpc import SRPC

def servHandler(service):
    while True:
        query = service.query()
        print query.query
        query.connection.response("OK")


def main(argv):
    host = "localhost"
    port = "20000"
    service = "HWDB"
    myService = "handler"

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
    # data, addr = srpc.sock.recvfrom(1024)
    # p = Payload(buffer=data)
    # print p.toString(), "len:", len(data)
    # srpc.sock.sendto(data,
    #                  ("127.0.0.1", 5000))
    serv = srpc.offerService(myService)
    print serv.name
    serv_t = Thread(target=servHandler, args=(serv,))
    serv_t.start()

    conn = srpc.connect("localhost", 5000, "HWDB")
    print "Connection to {}@{}:{} - {}".format(service, host, port, "connected" if conn is not None else "failed")
    if conn is None:
        srpc.close()
        sys.exit(-1)

    print "Sending:  SQL:create table b (i integer, r real)"
    response = conn.call("SQL:create table b (i integer, r real)")
    if response is not None:
        print "We received:", response
    print "Sending: SQL:insert into b values ('5', '5.0')"
    response = conn.call("SQL:insert into b values ('5', '5.0')")
    if response is not None:
        print "We received:", response

    print "Registering automaton"
    response = conn.call('SQL:register "subscribe t to Timer;\rbehavior {{\r  send(t);\r}}" {} {} {}'.format("127.0.0.1", srpc.port, myService))
    if response is not None:
        print "We received:", response

    # response = conn.call("BULK:72\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\ninsert into b values ('5', '5.0')\n")
    # if response is not None:
    #     print "We received:", response




if __name__ == '__main__':
    main(sys.argv)
