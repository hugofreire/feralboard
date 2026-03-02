#!/bin/bash
# Send a command to the Feralboard Workbench app via Unix socket
# Usage: bash send.sh navigate outputs
#        bash send.sh click 100 200
#        bash send.sh page
echo "$*" | socat - UNIX-CONNECT:/tmp/feralboard-workbench.sock
