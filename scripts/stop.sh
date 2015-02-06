#!/bin/bash

# Stop EKG server
kill $(ps aux | grep '[p]ython ../examples/ekg/sample_server.py' | awk '{print $2}')
