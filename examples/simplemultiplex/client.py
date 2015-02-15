import sephiroth
import time
import socket

c1    = sephiroth.endpoint('unique_client_id1')
c2    = sephiroth.endpoint('unique_client_id2')
cfail = sephiroth.endpoint('unique_client_id1')

print 'Connecting..'
while True:
    try:
        c1.connect('localhost', 7771)
        c2.connect('localhost', 7771)
        cfail.connect('localhost', 7771)
        break
    except socket.error:
        print('Error connecting retrying in 3...')
        time.sleep(3)
    except sephiroth.EndpointExists as ee:
        print('Error endpoint exists: %s' % ee.message)
        break

print 'Sending..'
c1.send('mensaje 1')
c1.send('mensaje 2 some more data sent')
c1.send('mensaje 3 wooooot')

c2.send('mensaje 1')
c2.send('mensaje 2 some more data sent')
c2.send('mensaje 3 wooooot')
