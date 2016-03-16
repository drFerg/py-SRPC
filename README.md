# py-SRPC
A python port of the simple RPC ([SRPC](https://github.com/jsventek/SRPC "SRPC C lib git")) system for connecting to the HWDB [Cache](https://github.com/jsventek/Cache "Cache git") instances.


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

For a bigger example check out [hwdb.py](https://github.com/fergul/py-SRPC/blob/master/hwdb.py "hwdb example"), which shows:
 - connecting to a HWDB Cache instance
 - creating a table, inserting
 - registering an automaton and listening for responses

