import threading
import os
import sephiroth
import logging
from tornado import websocket
from tornado import web, httpserver, ioloop


WS_PORT= 7771
log    = logging.getLogger('sephiroth_ws')


class SephirothWebSocket(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(SephirothWebSocket, self).__init__(application, request, **kwargs)
        self.is_open = False

    def open(self):
        self.is_open = True
        log.info('Wound open...')

    def on_message(self, message):
        def handle_fn(msg):
            id_client = msg
            try:
                pin, pout = os.pipe()
                sephiroth.add_pipe(id_client, pout)
            except sephiroth.ClientNotFound:
                self.close()
                log.warn('Client %s is not connected' % id_client)
                return
                
            while 1:
                if not self.is_open: break
                data = os.read(pin, sephiroth.MSGLEN)
                try:
                    log.info('WS write: %s' % data)
                    self.write_message(data)
                except websocket.WebSocketClosedError:
                    log.error('WS Closed error')
                    break
            # TODO Look for edge cases where this line may not be executed
            # This could be a source of a memory leak
            sephiroth.remove_pipe(id_client, pout)
            self.close()
        if message == 'stop':
            self.is_open = False
        else:
            t = threading.Thread(target=handle_fn, args=(message, ))
            t.start()

    def on_close(self):
        self.is_open = False
        log.info('Closing..')


def ws_start():
    application = web.Application([
        (r'/sephiroth', SephirothWebSocket),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_PORT)
    ioloop.IOLoop.instance().start()
