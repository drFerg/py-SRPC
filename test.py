import connectPayload, dataPayload

a = connectPayload.ConnectPayload()
a.command = 1
a.seqno = 10
a.service = "hello"
b = a.pack()
print len(b)
c = connectPayload.ConnectPayload(buffer=b)
print c.toString()

d = dataPayload.DataPayload(data_len=10, frag_len=10, data="Hello")
print d.toString()
b = d.pack()
e = dataPayload.DataPayload(buffer=b)
print e.toString()
