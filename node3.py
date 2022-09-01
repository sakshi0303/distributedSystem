from concurrent.futures import thread
import logging
import time
from node import Node
import random

def messageHandler(node):
    node.sendMessage(18081, "Dummy message from port Node3 to Node1")    
    pass    
    
if __name__=='__main__':
    random_value = float(random.randint(1.0, 20.0))
    n1 = Node(18083, 2, [0,0,random_value])
    time.sleep(4)
    n1.synchronize(18888)
    while n1.isSynchronized!=True:
        time.sleep(15)

    logging.info("node3 synchronised")
    n1.readMessage(messageHandler)
