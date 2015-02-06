import threading
import os
import sephiroth
import logging
from tornado import websocket
from tornado import web, httpserver, ioloop
from collections import deque

# For heart rate calculation
import numpy as np
from scipy import signal

# Default variables
WS_PORT   = 7771

# For hr calculation
SAMPLING_HZ = 50
CLIENT_DATA = {}

log = logging.getLogger('sephiroth_ws')

def get_values(data):
    values = data.split(';')
    return float( values[0] ), float( values[1] )

def set_client_data(client_id, data):
    datalist        = CLIENT_DATA.get(client_id, None)
    time_val, value = get_values(data)
    
    if datalist:
        datalist.append(value)
    else:
        # We need max length to be the number of samples in 6 seconds
        # To calculate heart rate which is 10*num_of_peaks_in_6_seconds
        maxlen = 6 * SAMPLING_HZ
        CLIENT_DATA[client_id] = deque([value], maxlen=maxlen)

def get_heart_rate(client_id):
    data = CLIENT_DATA.get(client_id, None)
    if data:
        try:
            num_peaks = signal.find_peaks_cwt(
                data, 
                np.arange(10, 20)
            )
            return len(num_peaks) * 10
        except ValueError:
            # TODO fix this!
            return 60
    return 0

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
                set_client_data(id_client, data)
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
    ws.write_message( '%d' % get_heart_rate(client_id) )

def get_handler(handle_msg):
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
        (r'/sephiroth', get_handler(handle_signal)),
        (r'/sephiroth_hr', get_handler(handle_heartrate)),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_PORT)
    ioloop.IOLoop.instance().start()

