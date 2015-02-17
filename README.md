#sephiroth
**Messaging multiplexing library for python**

Sephiroth is a library for simple message multiplexing. 
It was designed for the construction of an EKG signal distribution server, as a graduation project for the Computer Science department of the ESPOL.

The library defines an `endpoint` class, which instances can handle connections as client or server. Here is an example:

```python
import sephiroth

def fn1(conn, uid, msg):
    print('Message <%s> handled by fn1 from client <%s>')

server = sephiroth.endpoint('Example server')
server.bind('localhost', 7777)
```

###Dependencies for running EKG example
 - python 2.7.6+
 - node
 - npm
 - bower
 - gulp
 - tornado
 - numpy
 - scipy


###Steps for setting up EKG example
 1. Install python and pip
 2. Download and install nodejs [here](http://nodejs.org/download/)
 3. Clone this repo 
     `git clone https://github.com/phasnox/sephiroth.git`
 4. Checkout eksampling branch 
     `cd sephiroth && git checkout eksampling`
 5. If you are on Debian run 
     `bash scripts/ekg_setup.sh`
 6. Install python dependencies

     ```bash
     #Python dependencies
     sudo pip install tornado
     sudo pip install numpy
     sudo pip install scipy
     ```
     
 7. Install bower and gulp

     ```bash
     # Dependencies for the webapp
     cd examples/ekg/frontend
     sudo npm install -g bower
     sudo npm install -g gulp
     bower install
     npm install gulp
     gulp
     ```

###Run the sample server
 `bash scripts/start.sh`
This will run a server on http://localhost:9000/

####Loading a datalog
If you wish to load and display a datalog:
 1. Datalog must be a text file with a list of values.
 2. Put your in the folder data/
 3. Go to http://localhost:9000/
 4. Insert your filename as Client Id.
 5. Set the sampling frequency in hertz
 6. Press the <- Button
