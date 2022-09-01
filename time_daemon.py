import threading
import socket
import time
import random
import signal


local_clock = random.randrange(1, 100)
connected_nodes = {}
exit_event = threading.Event()


def signal_handler(signum, frame):
    print('received exit event')
    exit_event.set()


def pollConnectedNodesForTime(connector, address):

    while True:
        if exit_event.is_set():
            exit()
        try:
            raw_clock = connector.recv(1024).decode()
            clock_time = float(raw_clock)

            connected_nodes[address] = {
                "clock": clock_time,
                "connector": connector
            }
        except:
            connected_nodes.pop(address, {})
        time.sleep(10)


def connectToOtherNodes(daemon_server):
    while True:
        if exit_event.is_set():
            exit()
        # start accepting connections from other nodes
        connector, addr = daemon_server.accept()
        slave_address = str(addr[0]) + ":" + str(addr[1])

        print(slave_address + " got connected successfully")

        thread = threading.Thread(
            target=pollConnectedNodesForTime,
            args=(connector,
                  slave_address, ))
        thread.start()


def initiateClockServer(connection_port):
    daemon_server = socket.socket()
    daemon_server.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)
    print("time daemon node created successfully\n")

    daemon_server.bind(('', connection_port))
    daemon_server.listen(10)
    print("time daemon is up and running...\n")
    print("time daemon start listening to other nodes...\n")
    master_thread = threading.Thread(
        target=connectToOtherNodes,
        args=(daemon_server, ))
    master_thread.start()
    # start synchronization

    time.sleep(10)
    print("start synchronization...\n")
    sync_thread = threading.Thread(
        target=synchronizeAllClocks,
        args=())
    sync_thread.start()


# subroutine function used to fetch average clock difference
def getAverageClock():

    node_clocks = list(client['clock']
                       for _, client
                       in connected_nodes.items())

    # print('node_clocks')
    # print(node_clocks)

    aggregated_time = sum(node_clocks) + local_clock

    # print('aggregated_time')
    # print(aggregated_time)

    average_clock = round((aggregated_time / (len(connected_nodes)+1)), 2)

    
    return average_clock


def getSkew(clock, average):
    return round(average - clock, 2)    

def synchronizeAllClocks():

    global local_clock
    while True:
        if exit_event.is_set():
            exit()
        print("\n \n New synchronization cycle started. \n")
        print("Number of connected nodes to be synchronized: " +
              str(len(connected_nodes)))

        if len(connected_nodes) > 0:
            average_clock = getAverageClock()
            print('local clock before sync ' + str(local_clock))
            temp = round(local_clock + getSkew(local_clock, average_clock), 2)
            local_clock = temp
            print('local clock set to ' + str(local_clock))

            for client_addr, client in connected_nodes.items():
                try:
                    synchronized_time = getSkew(client['clock'], average_clock)
                    print('skew of ' + str(client_addr) +
                          ' is ' + str(synchronized_time))
                    try:
                        client['connector'].send(
                            str(synchronized_time).encode())
                    except:
                        print('failed to send to ' + str(client_addr))
                        client['clock'] = local_clock
                except Exception as e:
                    print("Something went wrong while " +
                          "sending synchronized time " +
                          "through " + str(client_addr))
                    connected_nodes.pop(client_addr)

        else:
            print("No client data." +
                  " Synchronization not applicable.")

        time.sleep(10)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    # start the time daemon
    print('local clock of daemon server ' + str(local_clock))
    connection_port = 18888
    request_processor = threading.Thread(
        target=initiateClockServer, args=(connection_port,))
    request_processor.start()
    # initiateClockServer(connection_port)
    print('server listening on port ', connection_port)
