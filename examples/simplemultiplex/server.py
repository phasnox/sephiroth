import sephiroth
import threading
import argparse
import os
import time

def main():
    s = sephiroth.endpoint('server_id')
    t = threading.Thread(target=s.bind, args=('localhost', 7771))
    t.start()

    while not s.alive:
        pass

    def get_handle_function(fn_name):
        def handle_function(conn, uid, msg):
            print('Handle by <%s>, Client id: <%s>, Message: <%s>') % (fn_name, uid, msg)

        return handle_function

    handle1 = get_handle_function('handle1')
    handle2 = get_handle_function('handle2')

    # Client 1
    s.add_handler('unique_client_id1', handle1)
    s.add_handler('unique_client_id1', handle2)

    # Client 2
    s.add_handler('unique_client_id2', handle1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--host', help='host name or ip v')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or ''
    port = args.port or 7771
    try:
        print 'Sephiroth awake..'
        main()
        while 1:
            time.sleep(5000)
    except KeyboardInterrupt:
        print '\nSephiroth fainted..'
        os._exit(0)

