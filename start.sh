#!/bin/bash

#killing the existing processes.
#kill $(ps aux | grep 'time_daemon.py' | grep -v grep | awk '{print $2}') 
kill $(ps aux | grep 'node1.py' | grep -v grep | awk '{print $2}') 
kill $(ps aux | grep 'node2.py' | grep -v grep | awk '{print $2}')
kill $(ps aux | grep 'node3.py' | grep -v grep | awk '{print $2}')
# &> writes log to a file
# & in the end of the script runs the process in background

nohup bash -c "python3 -u node1.py" &>node1.log &
nohup bash -c "python3 -u node2.py" &>node2.log &
nohup bash -c "python3 -u node3.py" &>node3.log &
# #sleep(5)
