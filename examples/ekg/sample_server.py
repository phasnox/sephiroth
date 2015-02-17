import sephiroth
import ekg_ws
import ekg_helpers
import threading
import os
import time
import argparse

CLIENT_DATA = {}

# TODO Find a way to get the call CLIENT_DATA[uid] out of this method
def add_cache(conn, uid, msg):
    data = CLIENT_DATA.get(uid, None)
    point= ekg_helpers.get_values(msg)
    if data is not None:
       data.append(point)
    else:
        CLIENT_DATA[uid] = [point]

def main(host, port):
    try:
        sephiroth_endpoint   = sephiroth.endpoint('ekg_server', timeout=5)
        sephiroth_endpoint.add_handler('*', add_cache)
        thread_signal_server = threading.Thread(target=sephiroth_endpoint.bind, args=(host, port))
        thread_signal_server.start()

        # Wait until sephiroth comes alive
        while not sephiroth_endpoint.alive:
            pass

        thread_websocket_server = threading.Thread(target=ekg_ws.ws_start, args=(sephiroth_endpoint, CLIENT_DATA))
        thread_websocket_server.start()
        print 'Sephiroth awake..'
        while 1:
            time.sleep(300)
    except KeyboardInterrupt:
        print '\nSephiroth fainted..'
        os._exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--host', help='host name or ip v')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or ''
    port = args.port or 7777
    main(host, port)
