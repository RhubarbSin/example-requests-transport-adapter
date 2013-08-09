#!/usr/bin/env python
"""This example of a transport adaptor for Requests supports
specification of a source address for Requests connections.
"""

import sys
try:
    from http.client import HTTPSConnection
except ImportError:
    from httplib import HTTPSConnection

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import PoolManager, HTTPSConnectionPool

class MyAdapter(HTTPAdapter):

    """This transport adapter and the supporting subclasses of
    PoolManager and HTTPSConnectionPool support specifying a source
    address via keyword arg "src_addr" ultimately propagated to the
    socket creation (requires "source_address" arg added to
    HTTPSConnection in Python 2.7).
    """

    def __init__(self, *args, **kwargs):
        # src_addr MUST be a keyword arg
        self.src_addr = kwargs.pop('src_addr', None)
        super(MyAdapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['src_addr'] = self.src_addr
        self.poolmanager = MyPoolManager(*args, **kwargs)

class MyPoolManager(PoolManager):

    def __init__(self, *args, **kwargs):
        self.src_addr = kwargs.pop('src_addr', None)
        super(MyPoolManager, self).__init__(*args, **kwargs)

    def _new_pool(self, scheme, host, port):
        kwargs = self.connection_pool_kw
        if scheme == 'http':
            kwargs = self.connection_pool_kw.copy()
            for kw in SSL_KEYWORDS:
                kwargs.pop(kw, None)
        kwargs['src_addr'] = self.src_addr
        return MyHTTPSConnectionPool(host, port, **kwargs)

class MyHTTPSConnectionPool(HTTPSConnectionPool):

    def __init__(self, *args, **kwargs):
        self.src_addr = kwargs.pop('src_addr', None)
        super(MyHTTPSConnectionPool, self).__init__(*args, **kwargs)

    def _new_conn(self):
        # original method is more elaborate (uses VerifiedHTTPSConnection)
        self.num_connections += 1
        source_address = (self.src_addr, 0) if self.src_addr else None
        return HTTPSConnection(host=self.host,
                               port=self.port,
                               strict=self.strict,
                               source_address=source_address)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        url = 'https://google.com'
    elif len(sys.argv) == 3:
        url = sys.argv[2]
    else:
        print 'Usage: %s LOCAL_IP_ADDRESS [URL]' % sys.argv[0]
        sys.exit(2)
    source_address = sys.argv[1]
    session = requests.Session()
    session.mount('https://', MyAdapter(src_addr=source_address))
    response = session.get(url)
    print response.status_code
