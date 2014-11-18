import socket
import select
import ssl
import os
#from pprint import pprint
from urlparse import urlparse, uses_netloc
uses_netloc.append('rendezvous')


class InvalidResponseFromRendezVous(Exception):
    pass


class Rendezvous():
    def __init__(self, url, printout=False):
        self.url = url
        urlp = urlparse(url)
        self.hostname = urlp.hostname
        self.port = urlp.port
        self.secret = urlp.path[1:]
        path = os.path.dirname(os.path.realpath(__file__))
        self.cert = os.path.abspath("{0}/data/cacert.pem".format(path))
        self.data = ""
        self.printout = printout

    def start(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Require a certificate from the server. We used a self-signed certificate
        # so here ca_certs must be the server certificate itself.

        ssl_sock = ssl.wrap_socket(s,
                            ca_certs=self.cert,
                            cert_reqs=ssl.CERT_REQUIRED,
                            ssl_version=ssl.PROTOCOL_TLSv1)

        ssl_sock.settimeout(20)
        ssl_sock.connect((self.hostname, self.port))
        ssl_sock.write(self.secret)
        data = ssl_sock.read()
        if not data.startswith("rendezvous"):
            raise InvalidResponseFromRendezVous("The Response from the rendezvous server wasn't as expected. Response was - {0}".format(data))
        while True:
            r, w, e = select.select([ssl_sock], [], [])
            if ssl_sock in r:
                try:
                    data = ssl_sock.recv(1024)
                except ssl.SSLError as e:
                    # Ignore the SSL equivalent of EWOULDBLOCK, but re-raise other errors
                    if e.errno != ssl.SSL_ERROR_WANT_READ:
                        raise e
                    continue
                # No data means end of file
                if not data:
                    break
                if self.printout:
                    print data.rstrip('\n')
                self.data += data
        return self.data
