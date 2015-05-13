import socket
import select
import errno
import threading
import logging

log           = logging.getLogger('sephiroth')
MSG_SEPARATOR = '\n'
log.setLevel(logging.INFO)

# Exceptions for flow control
class WrongUID(Exception):
    pass

class EndpointExists(Exception):
    pass

class SephirothReadError(Exception):
    pass

class STATE:
    CONNECTED       = '0'
    ENDPOINT_EXISTS = '1'
    WRONG_UID       = '2'

# Read all method to read from socket
def readall(sock, timeout=None):
    sock.setblocking(0)
    msg = []
    read_ready, _, _ = select.select([sock], [], [], timeout)
    if sock in read_ready:
        while True:
            try:
                chunk = sock.recv(1)
                if not chunk or chunk == MSG_SEPARATOR:
                    break
                msg.append(chunk)
            except socket.error as e:
                if e.errno != errno.EWOULDBLOCK:
                    raise SephirothReadError
                # No more data
                break
    return ''.join(msg)

# Endpoint class
# ---------------
class endpoint:

    ''' Endpoint class '''
    def __init__(self, uid, timeout=None):
        self.uid       = uid
        self.alive     = False
        self.endpoints = []
        self.handlers  = {'*': []}
        self.timeout   = timeout
        self.sock  = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __handle_conn(self, conn, addr):
        
        def handle_thread(conn, addr):
            # Check for uid
            uid = readall(conn, self.timeout)
            if uid in self.endpoints:
                log.error('uid exists :(')
                conn.sendall(STATE.ENDPOINT_EXISTS)
                conn.close()
                return

            if not uid or uid=='*':
                log.error('Wrong uid :(')
                conn.sendall(STATE.WRONG_UID)
                conn.close()
                return

            
            self.endpoints.append(uid)
            conn.sendall(STATE.CONNECTED)
            log.info('Client %s connected' % uid)

            handlers        = self.handlers.get(uid, None)
            global_handlers = self.handlers.get('*')
            while True:
                msg = readall(conn, self.timeout)
                if not msg: break
                if global_handlers:
                    for fn in global_handlers:
                        fn(conn, uid, msg)
                if handlers:
                    for fn in handlers:
                        fn(conn, uid, msg)
                else:
                    # This was added to avoid a possible race condition with
                    # method add_handler
                    handlers = self.handlers.get(uid, None)

            log.info('Removing %s' % uid)
            self.endpoints.remove(uid)
            conn.close()


        t = threading.Thread(target=handle_thread, args=(conn, addr))
        t.start()
        return t

    def bind(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.alive = True

        while True:
            conn, addr = self.sock.accept()
            self.__handle_conn(conn, addr)

        self.alive = False

    def connect(self, host, port):
        self.sock.connect((host, port))
        self.send(self.uid)
        response = readall(self.sock, self.timeout)
        if(response == STATE.CONNECTED):
            self.alive = True
            return
        if(response == STATE.ENDPOINT_EXISTS):
            raise EndpointExists
        if(response == STATE.WRONG_UID):
            raise WrongUID

    def remove_handler(self, uid, handler):
        handlers = self.handlers.get(uid, None)
        handlers.remove(handler)

    def add_handler(self, uid, handler):
        handlers = self.handlers.get(uid, None)
        if handlers is None:
            handlers = self.handlers[uid] = []
        handlers.append(handler)

    def send(self, msg):
        self.sock.sendall(msg + '\n')
