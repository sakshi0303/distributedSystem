## Part 2: Implement vector algorithm to sync node clocks

### Dependencies
- Python 3.8.10

### Steps to run the code
- install python3
- install pip3
- install randomtimestamp

- run 1st script file in one terminal
    - python3 time_daemon.py
    
-run another script in another terminal
    - sh start.sh

- 3 log file will be created.( node1.log,node2.log,node3.log)

start.sh script will delete all the existing processess running in backgraound and it will start 3 independednt nodes with there log files

this will initiate a message forward loop to demonstrate and dsiplay vector clock state when a message is received and sent by a node

Message flow:

1. node1->node2->node3 
2. node1->node3




time_daemon port: 18888
node1 port:18081
node2 port:18082
node3 port:18083