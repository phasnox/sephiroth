# -*- encoding: utf-8 -*-
import time
import math
import sephiroth
import argparse
import socket
from datetime import datetime
import random

# This indicates how many times the signal is read
READ_FREQUENCY = 200  # Frequency in Hz
RFQ            = float(1)/float(READ_FREQUENCY) # In seconds

def send_data(client, signal):
    data = '{time:%Y-%m-%dT%H:%M:%S.%fZ};{signal:07.2f}' \
            .format(time=datetime.now(), signal=signal)
    client.send(data)

import os
def start(client_id, host, port):
    client    = sephiroth.endpoint(client_id)
    while True:
        try:
            client.connect(host, port)
            break
        except socket.error:
            print 'Attempt to reconnect in 3 seconds...'
            time.sleep(3)
    
    print 'Client %s connected' % client_id
    sdir    = os.path.dirname(os.path.realpath(__file__))
    filepath= os.path.join(sdir, 'data/' + client_id)
    while 1:
        with open(filepath, 'read') as f:
            for line in f:
                time.sleep(RFQ) # Read frequency
                signal = float(line.rstrip())
                send_data(client, signal/255)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--client', help='client id')
    parser.add_argument('-o', '--host', help='host name or ip address')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    client_id = args.client or '000000000000000'
    host      = args.host or 'localhost'
    port      = args.port or 7777
    start(client_id, host, port)
