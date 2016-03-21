# py-SRPC
A python port of the simple RPC ([SRPC](https://github.com/jsventek/SRPC "SRPC C lib git")) system for connecting to the HWDB [Cache](https://github.com/jsventek/Cache "Cache git") instances.


Install
-------

Prerequisites: pip

Just run:
```
$ python setup.py install
```

The srpc module will become available for use along with hwdb.py and
echoClient.py scripts

```
$ echoClient.py -h <host> -p <port> -s <service>
or
$ hwdb.py -h <host> -p <port> -s <service>
```


Example
-------
```python
from srpc import SRPC

srpc = SRPC(port=5001)
conn = srpc.connect("localhost", 5000, "service")
response = conn.call("Some query")
conn.disconnect()
srpc.close()
```

For a bigger example check out [hwdb.py](https://github.com/fergul/py-SRPC/blob/master/bin/hwdb.py "hwdb example"), which shows:
 - connecting to a HWDB Cache instance
 - creating a table, inserting
 - registering an automaton and listening for responses
