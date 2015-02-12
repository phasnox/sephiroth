import threading
import os
import logging
import json
from collections import deque
from datetime import datetime
from tornado import websocket
from tornado import web, httpserver, ioloop

# For heart rate calculation
import numpy as np
from scipy import signal

import ekg_helpers
import sephiroth
# Default variables
WS_PORT   = 7771

# For hr calculation
CLIENT_DATA = {}
CACHE_SIZE  = 1000000

log = logging.getLogger('sephiroth_ws')

def set_client_data(client_id, data):
    datalist = CLIENT_DATA.get(client_id, None)
    point    = ekg_helpers.get_values(data)
    
    if datalist:
        datalist.append(point)
    else:
        CLIENT_DATA[client_id] = [point]

def get_heart_rate(client_id):
    data = CLIENT_DATA.get(client_id, None)
    if data:
        try:
            # We need max length to be the number of samples in 6 seconds
            # To calculate heart rate which is 10*num_of_peaks_in_6_seconds
            nrecords = 6 * ekg_helpers.SAMPLING_HZ * -1
            data     = [x['value'] for x in data[nrecords:]]
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
                ws.write_message( data )
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


def get_data(client_id, from_point, n_records):
    data = CLIENT_DATA.get(client_id, None)
    if data is None:
        data    = [ float(line.rstrip()) for line in open('data/' + client_id, 'read') ]
        max_val = max(data)
        ref_time= datetime.now()
        data    = [{
            'time': ekg_helpers.get_time_str(i, ref_time), 
            'value': x/max_val}
            for i, x in enumerate(data)]
        CLIENT_DATA[client_id] = data

    i = ekg_helpers.find_index(data, from_point)
    if n_records<0:
        n_records = n_records*-1
        top = i
        i   = i - 2*n_records
        if i<0: 
            i = 0
            n_records = top

    return CLIENT_DATA[client_id][i:(i+n_records)]
        
def handle_history(ws, message):
    message_split = message.split(';')
    if len(message_split) != 3:
        ws.close()
        return

    client_id  = message_split[0]
    from_point = ekg_helpers.str_to_time(message_split[1])
    n_records  = int(message_split[2])
    data       = get_data(client_id, from_point, n_records)

    ws.write_message( json.dumps(data) )

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

