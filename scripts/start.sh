#!/bin/bash
export PYTHONPATH=$(pwd)

# Start EKG server
SERVERPID=$(ps aux | grep '[p]ython examples/ekg/sample_server.py' | awk '{print $2}')
if [ ! -z $SERVERPID ]; then
    echo "Killing existing server $SERVERPID.."
    kill $SERVERPID
fi

echo "Starting.."
python examples/ekg/sample_server.py &

# Start WebServer
(cd examples/ekg/frontend && gulp serve)
