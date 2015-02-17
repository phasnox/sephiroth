#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

ssh root@192.168.7.2 'mkdir -p sephiroth'
scp $DIR"/../../../sephiroth.py" $DIR"/../../../examples/ekg/client_bbb.py" root@192.168.7.2:sephiroth/
scp $DIR"/bbb_init_script" root@192.168.7.2:/etc/init.d/ekg
