import sephiroth
import ekg_ws
import threading
import os
import socket
import sys
import argparse

DATA=[]

def handle_fn(ip, msg):
    pass #print 'Mensaje recibido de %s: %s' % (ip, msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--host', help='host name or ip v')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or ''
    port = args.port or sephiroth.DEFAULT_PORT
    try:
        s = sephiroth.Server(handle_fn, host=host, port=port)
        tsephiroth   = threading.Thread(target=s.serve_forever)
        tsephiroth.start()

        tsephirothws = threading.Thread(target=ekg_ws.ws_start)
        tsephirothws.start()
        
        print 'Sephiroth awake..'
        while 1:
            pass
    except KeyboardInterrupt:
        print '\nSephiroth fainted..'
        os._exit(0)
