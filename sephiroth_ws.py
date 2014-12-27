import threading
import os
from tornado import websocket
from tornado import web, httpserver, ioloop
from sephiroth import PIPES, MSGLEN


WS_PORT= 7771
log    = logging.getLogger('sephiroth_ws')


class SephirothWebSocket(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(SephirothWebSocket, self).__init__(application, request, **kwargs)
        self.is_open      = False

    def open(self):
        self.is_open = True
        log.info('Wound opened...')

    def on_message(self, message):
        def handle_fn(msg):
            ip_address  = msg
            pin, pout   = os.pipe()
            pipe = PIPES.get(ip_address, None)
            if pipe is not None:
                pipe.append(pout)
            else:
                self.close()
                return
            while 1:
                if not self.is_open: break
                data = os.read(pin, MSGLEN)
                try:
                    print 'WS write: %s' % data
                    self.write_message(data)
                except websocket.WebSocketClosedError:
                    log.error('WS Closed error')
                    break
            PIPES[ip_address].remove(pout)
            self.close()
        if message == 'stop':
            self.is_open = false
        else:
            t = threading.Thread(target=handle_fn, args=(message, ))
            t.start()

    def on_close(self):
        self.is_open = False
        print 'Closing..'
        log.info('Wound closed...')


def ws_start():
    application = web.Application([
        (r'/sephiroth', SephirothWebSocket),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_PORT)
    ioloop.IOLoop.instance().start()
