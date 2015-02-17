#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Add sephiroth dir to PYTHONPATH
export PYTHONPATH=$DIR"/../../../"
script_path=$DIR"/../sample_server.py"

# Kill existing server if exists
SERVERPID=$(ps aux | grep "[p]ython $script_path" | awk '{print $2}')
if [ ! -z $SERVERPID ]; then
    echo "Killing existing server $SERVERPID.."
    kill $SERVERPID
fi

# Start EKG server
echo "Starting Server.."
python $script_path &

# Start WebServer
(cd $DIR"/../frontend" && gulp serve)
