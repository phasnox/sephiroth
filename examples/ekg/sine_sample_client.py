# -*- encoding: utf-8 -*-
import time
import math
import sephiroth
import argparse
import socket
from datetime import datetime
import random

# This indicates how many times the signal is read
READ_FREQUENCY = 50  # Frequency in Hz
RFQ            = float(1)/float(READ_FREQUENCY) # In seconds
random_number  = random.randint(1,10)

def get_signal(t):
    return pow(math.sin(random_number*t), 2)

def send_data(client, signal):
    data = '{time:%Y-%m-%dT%H:%M:%S.%fZ};{signal:07.2f}' \
            .format(time=datetime.now(), signal=signal)
    client.send(data)

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
    count = 0.00
    while 1:
        count  = count + RFQ
        signal = get_signal(count)
        send_data(client, signal)
        time.sleep(RFQ) # Read frequency


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--client', help='client id')
    parser.add_argument('-o', '--host', help='host name or ip address')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    client_id = args.client or str(random_number)
    host      = args.host or 'localhost'
    port      = args.port or 7777
    start(client_id, host, port)
