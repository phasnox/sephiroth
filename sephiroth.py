import socket
import threading
import SocketServer
import os
import logging

MSGLEN          = 22
DEFAULT_PORT    = 7777
MAX_CONNECTIONS = 1000
CLIENT_LIST     = []
PIPES           = {}
CLIENT_PREFIX   = ''

log = logging.getLogger('sephiroth')


def _get_client_id(request_handler):
    return request_handler.client_address[0]

def get_handler(handle_fn, msg_len, get_client_id):
    
    class DRH(SocketServer.BaseRequestHandler):
        def handle(self):
            client_id = get_client_id(self)
            if client_id in CLIENT_LIST:
                log.warn('Client %s already connected' % client_id)
                self.request.sendall('')
                return
            else:
                pipes = PIPES.get(client_id, None)
                if not pipes:
                    log.info('Creating new list of pipes for %s' % client_id)
                    pipes = PIPES[client_id] = []
            while 1:
                data = self.request.recv(msg_len)
                if not data: break
                for pipe in pipes:
                    os.write(pipe, data)
                if handle_fn: handle_fn(self, data)
    return DRH


class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(
            self, 
            handle_fn, 
            get_client_id=_get_client_id, 
            msg_len=MSGLEN, 
            host=None, 
            port=None):
        ''' Initializes Sephiroth server '''
        host = '' if host is None else host
        port = DEFAULT_PORT if port is None else port
        SocketServer.TCPServer.__init__(
                self, (host, port), 
                get_handler(handle_fn, msg_len, get_client_id))

        
class Client:

    def __init__(self, sock=None, msg_len=MSGLEN):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.sock = sock
        self.msg_len = msg_len

    def connect(self, host, port=None):
        port = DEFAULT_PORT if port is None else port
        self.sock.connect((host, port))

    def send(self, msg):
        return self.sock.sendall(msg)

    def receive(self):
        return self.sock.recv(self.msg_len)


def add_client(client_id):
    return CLIENT_LIST.append(client_id)

def seek(client_id):
    '''Seek client in list of connected clients'''
    return client_id in CLIENT_LIST

def remove(client_id):
    '''Removes client from list of connected clients'''
    return CLIENT_LIST.remove(client_id)

