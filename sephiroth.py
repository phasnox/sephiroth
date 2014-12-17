import socket
import threading
import SocketServer
import logging
from tornado import websocket
from tornado import web, httpserver, ioloop
import os

MSGLEN          = 22
DEFAULT_PORT    = 7777
MAX_CONNECTIONS = 1000
CLIENT_LIST     = []
PIPES           = {}

log = logging.getLogger('sephiroth')

def get_handler(handle_fn):
    
    class DRH(SocketServer.BaseRequestHandler):
        def handle(self):
            client_ip = self.client_address[0]
            if client_ip in CLIENT_LIST:
                sephiroth.log.info('Ip %s address already connected' % ip_address)
                self.request.sendall('')
                return
            else:
                pipes = PIPES.get(client_ip, None)
                if not pipes:
                    pipes = PIPES[client_ip] = []
            while 1:
                data = self.request.recv(MSGLEN)
                if not data: break
                for pipe in pipes:
                    os.write(pipe, data)
                if handle_fn: handle_fn(client_ip, data)
    return DRH


class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, handle_fn, host=socket.gethostname(), port=DEFAULT_PORT):
        SocketServer.TCPServer.__init__(self, (host, port), get_handler(handle_fn))
        self.timeout = 5

        
class Client:

    def __init__(self, sock=None, msg_len=MSGLEN):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.sock = sock

    def connect(self, host, port=DEFAULT_PORT):
        self.sock.connect((host, port))

    def send(self, msg):
        return self.sock.sendall(msg)

    def receive(self):
        return self.sock.recv(MSGLEN)


def add_client(ip_address):
    return CLIENT_LIST.append(ip_address)

def seek(ip_address):
    '''Seek client in list of connected clients'''
    return ip_address in CLIENT_LIST

def remove(ip_address):
    '''Removes client from list of connected clients'''
    return CLIENT_LIST.remove(ip_address)




class SephirothWebSocket(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(SephirothWebSocket, self).__init__(application, request, **kwargs)
        self.is_open      = False

    def open(self):
        self.is_open = True
        log.info('Wound opened...')

    def on_message(self, message):
        if message == 'stop':
            self.is_open = false
        else:
            ip_address  = message
            pin, pout   = os.pipe()
            PIPES[ip_address].append(pout)
            while 1:
                if not self.is_open: break
                data = os.read(pin)
                self.write_message(data)
            self.close()

    def on_close(self):
        self.is_open = False
        log.info('Wound closed...')
