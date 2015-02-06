# -*- encoding: utf-8 -*-
import time
import math
import sephiroth
import argparse
import Adafruit_BBIO.ADC as ADC
import socket


ADC.setup()
# This indicates how many times the signal is read
# Este numero no deberia ser mayor a 25 que equivale a 40ms
# que es el tamaño mas pequeño en un EKG paper
READ_FREQUENCY = 100 # Frequency in Hz
RFQ            = float(1)/float(READ_FREQUENCY) # In seconds

def get_signal(t):
    return ADC.read('P9_38')

def send_data(client, time, signal):
    data = '{time:014.2f};{signal:07.2f}'.format(time=time, signal=signal)
    print data
    client.send(data)

def get_mac():
    from uuid import getnode as get_mac
    return get_mac()

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
        send_data(client, count, signal)
        time.sleep(RFQ) # Read frequency


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--host', help='host name or ip address')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or 'localhost'
    port = args.port or sephiroth.DEFAULT_PORT
    start(host, port)
