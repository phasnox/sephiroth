# -*- encoding: utf-8 -*-
import time
import math
import sephiroth
import argparse
import socket

# This indicates how many times the signal is read
READ_FREQUENCY = 50  # Frequency in Hz
RFQ            = float(1)/float(READ_FREQUENCY) # In seconds

def get_signal(t):
    return pow(math.sin(5*t), 2)

def send_data(client, signal):
    data = '{signal:07.2f}'.format(signal=signal)
    client.send(data)

def start(host, port):
    # Use mac address as client id
    client_id = '000000000000000' #get_mac()
    client    = sephiroth.Client(client_id)
    while True:
        try:
            client.connect(host=host, port=port)
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
    parser.add_argument('-o', '--host', help='host name or ip address')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or 'localhost'
    port = args.port or sephiroth.DEFAULT_PORT
    start(host, port)
