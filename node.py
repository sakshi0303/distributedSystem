from queue import Queue
import socket
import logging
import threading
import traceback
import time
import ast
from  collections import deque

format = "Node :%(asctime)s.%(msecs)03d: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt='%Y-%m-%d,%H:%M:%S')    


# historical_list=[0,1,2]
# historical_queue=deque(historical_list)

# <-------------------------------------------------------------<Node class>------------------------------------------------------------>
# Node class which starts listening when initialized
# Maintains a vector clock in a thread safe queue
class Node:
    listener : socket
    queue : Queue
    port : int
    index : int
    isSynchronized: bool
    vectorClock: list
    
    # constructor
    def __init__(self, port, index, vectorClock) -> None:                        
        self.queue = Queue()
        self.port = port
        self.index = index
        self.vectorClock = vectorClock
        self.isSynchronized = False
        # add initial vector clock to the queue
        self.queue.put(self.vectorClock)
        # start listening at port
        self.listen()
        # give listener time to start before other nodes start sending messages
        time.sleep(5)

    def _event(self):
        obj=self.queue.get()
        obj[self.index] +=1
        obj = list(map(int, obj))
        logging.info(f'event happened in {obj} !')
        self.queue.put(obj)
        #logging.info(f"After queue.put() size of the queue {queue.qsize()}")
        return obj


    def readFromQueue(self):
        # returns the first item in the queue
        obj = self.queue.get()        
        # queue.get will always remove first entry . 
        # If the queue is empty the get call will be block and will be keep on waiting for quue to have value
        self.queue.put(obj)
        return obj

    def writeToQueue(self, obj):
        # writing to the queue and replacing the old item
        self.queue.get()
        self.queue.put(obj)
        self.vectorClock = obj
        return obj

    def sendMessage(self, port, message):
        self._event()
        slave=socket.socket()
        slave.connect(('127.0.0.1', port))    
        message = self._encloseMessage(message)
        sendMessageThread=threading.Thread(target=self._sendMessage,args=(slave,message,))
        logging.info(f"sending a mesage {message}\n\n")
        sendMessageThread.start()
        return 0

    def _sendMessage(self, slave, message):
        nBytesSent = slave.send(str(message).encode())

    def _encloseMessage(self, message: str):    
        res = list(map(int, self.vectorClock))
        self.vectorClock = res    
        obj = {
            'port': self.port,
            'vectorClock': self.vectorClock,
            'message': message
        }
        return obj

    # read the message and perform callback function if message received
    # nothing happens if callback is None
    def readMessage(self, callback):
        receiveMessageThread = threading.Thread(target=self.accept, args=(callback,))
        receiveMessageThread.start()
        return 0

    def accept(self, callback):
        while True:
            conn,address=self.listener.accept()
            nodesAddress= str(address[0]) +":" +str(address[1])
            logging.info(f"{nodesAddress} ready to accept from other ports")
            # Socket will convert evrything into string - mapping data from string. 
            data = ast.literal_eval(conn.recv(1024).decode())        
              
            logging.info(f"data received : {data} ")

            if(data is not None):
                obj = self.readFromQueue()
                self._event()
                first = data['vectorClock']
                first = list(map(int, first)) 
                second = list(map(int, obj))            
                data['vectorClock'] = self._updateVectorClock(first, second)                
                logging.info(f"data after update: {data} \n\n")
                self.writeToQueue(data['vectorClock'])
                # event is called once before sending a message            
                if callback is not None:
                    # event is called within the send message (or callback) func                
                    callback(self)                
            time.sleep(2)

    def _updateVectorClock(self, first, second):
        for i in range(0, len(self.vectorClock)):
            first[i] = max(first[i], second[i])
        return first

    def listen(self):
        self.listener=socket.socket()
        self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        logging.info("Socket created\n")
        self.listener.bind(('', self.port))
        self.listener.listen(10)    
        logging.info("NodeListener started\n")


    def synchronize(self, port):
        sock = socket.socket()
        sock.connect(('127.0.0.1', port))
        send_time_thread = threading.Thread(
            target=self.sendLogicalClock,
            args=(sock, ))
        send_time_thread.start()

        logging.info("Starting to receiving synchronized time from server\n")
        receive_time_thread = threading.Thread(
            target=self.receiveLogicalClock,
            args=(sock, ))
        receive_time_thread.start()


    def receiveLogicalClock(self, sock):
        local_clock = self.readFromQueue()[self.index]
        while True:
            try:
                data = sock.recv(1024).decode()
                if(data!=''):
                    skew = round(float(data), 2)
                    logging.info("skew at the client is: " + str(skew))
                    temp = round(skew + float(self.readFromQueue()[self.index]), 2)
                                
                    # read and update vector clock
                    vector_clock = self.readFromQueue()                
                    vector_clock[self.index] = temp
                    self.writeToQueue(vector_clock)

                    if skew == 0.0:
                        self.isSynchronized = True 
                        break
                    logging.info('time of client set to ' + str(self.readFromQueue()[self.index]))
                else:
                    logging.info("received data is empty")
            except Exception as e:
                traceback.print_exc()                
                logging.info(f'Exception in receiving data : {e}')


    def sendLogicalClock(self,sock):        
        while True:
            local_clock = self.readFromQueue()[self.index]
            logging.info('sending local clock to time daemon ' + str(local_clock))
            sock.send(str(local_clock).encode())        
            time.sleep(10)

            if self.isSynchronized :
                break
