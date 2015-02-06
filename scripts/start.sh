#!/bin/bash
export PYTHONPATH=../$(pwd)

# Start EKG server
kill $(ps aux | grep '[p]ython ../examples/ekg/sample_server.py' | awk '{print $2}')
python ../examples/ekg/sample_server.py &

# Start WebServer
(cd ../examples/ekg/frontend && gulp serve)
