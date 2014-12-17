import os
import threading

pipein, pipeout = os.pipe()
def t1():
    msg = os.read(pipein, 5)
    print 'Thread 1 msg: %s' % msg

def t2():
    msg = os.read(pipein, 5)
    print 'Thread 2 msg: %s' % msg

t1 = threading.Thread(target=t1)
#t1.daemon = True
t1.start()

t2 = threading.Thread(target=t2)
#t2.daemon = True
t2.start()

os.write(pipeout, 'Hola\n')

