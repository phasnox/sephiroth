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

log = logging.getLogger('sephiroth_ws')

def get_heart_rate(client_id, data):
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
    
    def send_signal(conn, uid, msg):
        #if not ws.is_open: return
        try:
            ws.write_message( msg )
        except websocket.WebSocketClosedError:
            log.error('Client disconnected..')
            ws.sephiroth_endpoint.remove_handler(uid, send_signal)
    
    def handle_fn(msg):
        # A request comes with a client id we want to monitor
        id_client = msg
        ws.sephiroth_endpoint.add_handler(id_client, send_signal)

    if message == 'stop':
        ws.is_open = False
    else:
        t = threading.Thread(target=handle_fn, args=(message, ))
        t.start()


def handle_heartrate(ws, client_id):
    data = ws.client_data.get(client_id, None)
    ws.write_message( '%d' % get_heart_rate(client_id, data) )


def get_data(client_data, client_id, from_point, n_records):
    data = client_data.get(client_id, None)
    if data is None:
        data    = [ float(line.rstrip()) for line in open('data/' + client_id, 'read') ]
        max_val = max(data)
        ref_time= datetime.now()
        data    = [{
            'time': ekg_helpers.get_time_str(i, ref_time), 
            'value': x/max_val}
            for i, x in enumerate(data)]
        client_data[client_id] = data

    i = ekg_helpers.find_index(data, from_point)
    if n_records<0:
        n_records = n_records*-1
        top = i
        i   = i - 2*n_records
        if i<0: 
            i = 0
            n_records = top

    return data[i:(i+n_records)]
        
def handle_history(ws, message):
    message_split = message.split(';')
    if len(message_split) != 3:
        ws.close()
        return

    client_id  = message_split[0]
    from_point = ekg_helpers.str_to_time(message_split[1])
    n_records  = int(message_split[2])
    data       = get_data(ws.client_data, client_id, from_point, n_records)

    ws.write_message( json.dumps(data) )

def get_handler(handle_msg, sephiroth_endpoint=None, client_data=None):
    class SephirothWebSocket(websocket.WebSocketHandler):

        def __init__(self, application, request, **kwargs):
            super(SephirothWebSocket, self).__init__(application, request, **kwargs)
            self.is_open = False
            self.sephiroth_endpoint = sephiroth_endpoint
            self.client_data = client_data

        def open(self):
            self.is_open = True
            log.info('Wound open...')

        def on_message(self, message):
            handle_msg(self, message)

        def on_close(self):
            self.is_open = False
            log.info('Closing..')

    return SephirothWebSocket


def ws_start(sephiroth_endpoint, client_data):
    application = web.Application([
        (r'/sephiroth', get_handler(handle_signal, sephiroth_endpoint=sephiroth_endpoint)),
        (r'/sephiroth_hr', get_handler(handle_heartrate, client_data=client_data)),
        (r'/sephiroth_hist', get_handler(handle_history, client_data=client_data)),
    ])

    http_server = httpserver.HTTPServer(application)
    http_server.listen(WS_PORT)
    ioloop.IOLoop.instance().start()

