import threading
import os
import sephiroth
import logging
from tornado import websocket
from tornado import web, httpserver, ioloop
from collections import deque

WS_PORT   = 7771
WS_HR_PORT= 7772
log       = logging.getLogger('sephiroth_ws')
THRESHOLD     = 0.3
CLIENT_DATA   = {}
CLIENT_HR     = {}
CLIENT_PEAKS  = {}

def get_values(data):
    values = data.split(';')
    return float( values[0] ), float( values[1] )


def set_heartrate_data(client_id, data):
    hr              = 0
    datalist        = CLIENT_DATA.get(client_id, None)
    time_val, value = get_values(data)
    
    if datalist:
        datalist.append(value)
        datalength = float( len(datalist) )
        avg = float( sum(datalist) ) / datalength
        if value > avg * 1.75:
            elapsed = time_val - CLIENT_PEAKS.get(client_id, 0.0)
            if elapsed > THRESHOLD:
                CLIENT_PEAKS[client_id] = time_val
                CLIENT_HR[client_id]    = 60 / elapsed

    else:
        CLIENT_DATA[client_id] = deque([value], maxlen=300)
        CLIENT_HR[client_id]   = 0

def handle_signal(ws, message):
    def handle_fn(msg):
        id_client = msg
        try:
            pin, pout = os.pipe()
            sephiroth.add_pipe(id_client, pout)
        except sephiroth.ClientNotFound:
            ws.close()
            log.warn('Client %s is not connected' % id_client)
            return
            
        while 1:
            if not ws.is_open: break
            data = os.read(pin, sephiroth.MSGLEN)
            try:
                log.info('WS write: %s' % data)
                set_heartrate_data(id_client, data)
                ws.write_message(data)
            except websocket.WebSocketClosedError:
                log.error('WS Closed error')
                break
        # TODO Look for edge cases where this line may not be executed
        # This could be a source of a memory leak
        sephiroth.remove_pipe(id_client, pout)
        ws.close()

    if message == 'stop':
        ws.is_open = False
    else:
        t = threading.Thread(target=handle_fn, args=(message, ))
        t.start()


def handle_heartrate(ws, client_id):
    ws.write_message( '%.2f' % CLIENT_HR.get(client_id, 0.0) )

def get_ws(handle_msg):
    class SephirothWebSocket(websocket.WebSocketHandler):

        def __init__(self, application, request, **kwargs):
            super(SephirothWebSocket, self).__init__(application, request, **kwargs)
            self.is_open = False

        def open(self):
            self.is_open = True
            log.info('Wound open...')

        def on_message(self, message):
            handle_msg(self, message)

        def on_close(self):
            self.is_open = False
            log.info('Closing..')

    return SephirothWebSocket


def ws_start():
    application = web.Application([
        (r'/sephiroth', get_ws(handle_signal)),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_PORT)
    ioloop.IOLoop.instance().start()

def ws_hr_start():
    application = web.Application([
        (r'/sephiroth_hr', get_ws(handle_heartrate)),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_HR_PORT)
    ioloop.IOLoop.instance().start()
