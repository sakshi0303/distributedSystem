import logging
import threading
import time
from node import Node
import random
from concurrent.futures import thread

def messageHandler(node):    
    node.sendMessage(18083, "Dummy message from Node2 to Node3")    
    pass    
    
if __name__=='__main__':
    random_value = random.randint(1.0, 20.0)
    n1 = Node(18082, 1, [0,random_value,0])
    time.sleep(2)
    n1.synchronize(18888)
    while n1.isSynchronized!=True:
        time.sleep(15)

    logging.info("node2 synchronised")
    n1.readMessage(messageHandler)
