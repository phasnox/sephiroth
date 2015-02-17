#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Add sephiroth dir to PYTHONPATH
export PYTHONPATH=$DIR"/../../../"

# Start EKG server
python $DIR"/../sine_sample_client.py"
