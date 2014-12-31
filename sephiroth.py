import socket
import threading
import SocketServer
import os
import logging
from collections import deque

MSGLEN          = 22
DEFAULT_PORT    = 7777
MAX_CONNECTIONS = 1000
CLIENT_LIST     = deque()
PIPES           = {}
ID_CLIENT_LENGTH= 17 # MAC address length
log = logging.getLogger('sephiroth')


class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    ''' Server class to handle incoming signal '''
    def __init__(
            self, 
            handle_fn, 
            msg_len=MSGLEN, 
            id_client_len=ID_CLIENT_LENGTH, 
            host='', 
            port=DEFAULT_PORT):
        ''' Initializes Sephiroth server '''
        SocketServer.TCPServer.__init__( self, (host, port), 
                                        get_handler(handle_fn, msg_len, id_client_len))

        
class Client:

    ''' Client class to send signal to server '''
    def __init__(self, id, sock=None, msg_len=MSGLEN):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.sock = sock
        self.msg_len = msg_len
        self.id      = id

    def connect(self, host, port=DEFAULT_PORT):
        self.sock.connect((host, port))
        self.send(id)

    def send(self, msg):
        return self.sock.sendall(msg)

    def receive(self):
        return self.sock.recv(self.msg_len)


class ClientNotFound(Exception):
    pass


# ==================
# Helper functions
# ==================
def get_pipes(id_client):
    pipes = PIPES.get(id_client, None)
    if not pipes:
        raise ClientNotFound
    return pipes

def add_pipe(id_client, pipe):
    pipes = get_pipes(id_client)
    return pipes.append(pipe)

def remove_pipe(id_client, pipe):
    pipes = get_pipes(id_client)
    return pipes.remove(pipe)

def is_client_connected(id_client):
    return id_client in CLIENT_LIST

def add_client(id_client):
    return CLIENT_LIST.append(id_client)

def remove(id_client):
    '''Removes client from list of connected clients'''
    return CLIENT_LIST.remove(id_client)

def get_handler(handle_fn, msg_len, id_client_length):
    ''' Returns Default Request Handler(DRH) class for SocketServer '''
    class DRH(SocketServer.BaseRequestHandler):
        def handle(self):
            # First message is always the id
            id_client = self.request.recv(id_client_length)
            if is_client_connected(id_client):
                log.warn('Client %s already connected' % id_client)
                self.request.sendall('')
                return

            try:
                pipes = get_pipes(id_client)
            except ClientNotFound:
                # Client is new
                log.info('Creating new list of pipes for %s' % id_client)
                pipes = PIPES[id_client] = deque()
            while 1:
                data = self.request.recv(msg_len)
                if not data: break
                for pipe in pipes:
                    os.write(pipe, data)
                if handle_fn: handle_fn(self, data)
    return DRH
