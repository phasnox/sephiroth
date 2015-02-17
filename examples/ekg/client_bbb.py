# -*- encoding: utf-8 -*-
import time
import math
import sephiroth
import argparse
import Adafruit_BBIO.ADC as ADC
import socket
from datetime import datetime
import logging
logging.basicConfig()

log = logging.getLogger('client_bbb')
log.setLevel(logging.INFO)

ADC.setup()
# This indicates how many times the signal is read
READ_FREQUENCY = 50 # Frequency in Hz
RFQ            = float(1)/float(READ_FREQUENCY) # In seconds

def get_signal():
    return ADC.read('P9_38')

def send_data(client, signal):
    data = '{time:%Y-%m-%dT%H:%M:%S.%fZ};{signal:07.2f}' \
            .format(time=datetime.now(), signal=signal)
    client.send(data)

def start(client_id, host, port):

    def connect():
        while True:
            try:
                client = sephiroth.endpoint(client_id)
                client.connect(host=host, port=port)
                log.info('Client %s connected' % client_id)
                return client
            except socket.error as e:
                log.error(str(e))
                log.info('Attempt to reconnect in 3 seconds...')
                time.sleep(3)
    
    client = connect()
    while True:
        try:
            signal = get_signal()
            send_data(client, signal)
            time.sleep(RFQ) # Read frequency
        except socket.error:
            log.info('Client disconnected...')
            client = connect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--client', help='client id')
    parser.add_argument('-o', '--host', help='host name or ip address')
    parser.add_argument('-p', '--port', help='port number', type=int)

    args = parser.parse_args()
    client_id = args.client or '000000000000000'
    host      = args.host or '192.168.7.1'
    port      = args.port or 7777
    start(client_id, host, port)
