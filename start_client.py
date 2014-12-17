import time
import math
import sephiroth

# This indicates how many times the signal is read
READ_FREQUENCY = 1  # Frequency in Hz
RFQ            = 1/READ_FREQUENCY # In seconds


def get_voltage():
    t = time.time()
    return math.sin(t)

def send_data(client, v, t):
    data = '{time:014.2f};{voltage:07.2f}'.format(time=t, voltage=v)
    client.send(data)

def main():
    c = sephiroth.Client()
    c.connect('localhost')
    print 'Client connected'
    while 1:
        t = time.time()
        v = get_voltage()
        send_data(c, v, t)
        time.sleep(RFQ) # Read frequency


if __name__ == '__main__':
    main()
