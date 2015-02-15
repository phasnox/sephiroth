import sephiroth
import ekg_ws
import threading
import os
import argparse

def main(host, port):
    sephiroth_endpoint   = sephiroth.endpoint('ekg_server')
    thread_signal_server = threading.Thread(target=sephiroth_endpoint.bind, args=(host, port))
    thread_signal_server.start()

    # Wait until sephiroth comes alive
    while not sephiroth_endpoint.alive:
        pass

    thread_websocket_server = threading.Thread(target=ekg_ws.ws_start, args=(sephiroth_endpoint, ))
    thread_websocket_server.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--host', help='host name or ip v')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or ''
    port = args.port or 7777
    try:
        main(host, port)
        
        print 'Sephiroth awake..'
        while 1:
            pass
    except KeyboardInterrupt:
        print '\nSephiroth fainted..'
        os._exit(0)
