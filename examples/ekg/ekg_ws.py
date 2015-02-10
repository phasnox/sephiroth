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
SAMPLING_HZ   = 50
CLIENT_DATA   = {}
CACHE_SIZE    = 1000000

log = logging.getLogger('sephiroth_ws')

def get_values(data):
    return float( data )

def set_client_data(client_id, data):
    datalist  = CLIENT_DATA.get(client_id, None)
    value     = get_values(data)
    
    if datalist:
        datalist.append(value)
    else:
        CLIENT_DATA[client_id] = [value]

def get_heart_rate(client_id):
    data = CLIENT_DATA.get(client_id, None)
    if data:
        try:
            # We need max length to be the number of samples in 6 seconds
            # To calculate heart rate which is 10*num_of_peaks_in_6_seconds
            nrecords = 6 * SAMPLING_HZ * -1
            data     = data[nrecords:]
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
        del CLIENT_DATA[id_client]
        ws.close()

    if message == 'stop':
        ws.is_open = False
    else:
        t = threading.Thread(target=handle_fn, args=(message, ))
        t.start()


def handle_heartrate(ws, client_id):
    ws.write_message( '%d' % get_heart_rate(client_id) )

def get_data(client_id):
    data = CLIENT_DATA.get('data/' + client_id, None)
    if data is None:
        data    = [ float(line.rstrip()) for line in open(client_id, 'read') ]
        max_val = max(data)
        data    = [x/max_val for x in data]

    return data

def handle_history(ws, message):
    message_split = message.split(';')
    if len(message_split) != 3:
        ws.close()
        return

    client_id  = message_split[0]
    from_point = int(message_split[1])
    n_records  = int(message_split[2])
    data       = get_data(client_id)

    if data:
        if n_records > 500 or n_records<0: n_records = 500
        if from_point == -1: 
            return_data = data[n_records*-1:]
        else:
            return_data = data[from_point:n_records*-1]

        ws.write_message( return_data )

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
        (r'/sephiroth_hist', get_handler(handle_history)),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_PORT)
    ioloop.IOLoop.instance().start()

