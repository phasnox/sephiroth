#!/bin/bash

# Python dependencies
sudo pip install tornado
sudo pip install numpy
sudo pip install scipy

# Dependencies for the webapp
cd examples/ekg/frontend
npm install -g bower
npm install -g gulp
bower install
