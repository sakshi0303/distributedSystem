import logging
from platform import node
import random
from node import Node
import time
from concurrent.futures import thread


def messageHandler(node):

    
    #node.sendMessage(18082, "sakshi port 18082 from 18081")  
    # does not do anything on receivng a message from another node
    # if we send a message here it will lead to an endless cycle
    # we can limit this by using the vector clock index value to stop sending further messages
    pass    
    
if __name__=='__main__':
    
    random_value = random.randint(1.0, 20.0)
    n1 = Node(18081, 0, [random_value,0,0])

    n1.synchronize(18888)

    while n1.isSynchronized!=True:
        time.sleep(10)


    logging.info("node1 synchronised")
    n1.readMessage(None)
    n1.sendMessage(18082, "Dummy message from Node1 to port Node2 ")
    time.sleep(5)
    n1.sendMessage(18083, "Dummy message from Node1 to port Node3 ") 