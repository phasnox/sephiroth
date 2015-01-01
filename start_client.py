# -*- encoding: utf-8 -*-
import time
import math
import sephiroth
import argparse

# This indicates how many times the signal is read
# Este numero no deberia ser mayor a 25 que equivale a 40ms
# que es el tamaño mas pequeño en un EKG paper
READ_FREQUENCY = 25  # Frequency in Hz
RFQ            = float(1)/float(READ_FREQUENCY) # In seconds

def get_voltage(t):
    return math.sin(t)

def send_data(client, t, v):
    data = '{time:014.2f};{voltage:07.2f}'.format(time=t, voltage=v)
    print data
    client.send(data)

def get_mac():
    from uuid import getnode as get_mac
    return get_mac()

def start(host, port):
    client_id = get_mac()
    c = sephiroth.Client(client_id)
    c.connect(host=host, port=port)
    print 'Client %s connected' % client_id
    count = 0.00
    while 1:
        count = count + RFQ
        v = get_voltage(count)
        send_data(c, count, v)
        time.sleep(RFQ) # Read frequency


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--host', help='host name or ip address')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    host = args.host or 'localhost'
    port = args.port or sephiroth.DEFAULT_PORT
    start(host, port)
