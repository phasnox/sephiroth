#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
script_path=$DIR"/../sample_server.py"

echo $script_path
# Stop EKG server
SERVERPID=$(ps aux | grep "[p]ython $script_path" | awk '{print $2}')
if [ ! -z $SERVERPID ]; then
    echo "Killing existing server $SERVERPID.."
    kill $SERVERPID
fi
