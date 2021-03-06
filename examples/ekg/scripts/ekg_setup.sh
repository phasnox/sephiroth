#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

#Install dependencies for scipy
sudo apt-get install gfortran libopenblas-dev liblapack-dev

# Python dependencies
sudo pip install tornado
sudo pip install numpy
sudo pip install scipy

# Dependencies for the webapp
cd $DIR"/../frontend"
sudo npm install -g bower
sudo npm install -g gulp
bower install
npm install gulp
gulp
