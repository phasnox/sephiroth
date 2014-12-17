import sephiroth
import threading
import os
import socket
import sys


def sample_pipe():
    pin, pout = os.pipe()
    sephiroth.PIPES['127.0.0.1'] = [pout]
    while 1:
        sys.stdout.flush() 
        msg = os.read(pin, sephiroth.MSGLEN)
        print 'Sample pipe msg: %s' % msg


t1 = threading.Thread(target=sample_pipe)
t1.start()

def handle_fn(ip, msg):
    print 'Mensaje recibido de %s: %s' % (ip, msg)

if __name__ == '__main__':
    try:
        s = sephiroth.Server(handle_fn)
        print 'Sephiroth awake..'
        s.serve_forever()
    except KeyboardInterrupt:
        print '\nSephiroth fainted..'
        os._exit(0)
